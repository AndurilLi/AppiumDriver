"""
Contains methods to process page source got from Android and iOS.
"""
__author__ = 'Zhenyu'


import json
import copy
import re

translate_map_android = {
    "enabled": "@enabled",
    "visible": "@clickable",
    "hint": "@content-desc",
    "value": "@text",
    "label": "@text",
    "type": "@class",
    "checked": "@checked",
    "name": "@resource-id",
    "rect": "@bounds"
}


class PageSourceElementsTree(object):
    """
    constructing a tree from the page source data.json.
    we may use this for finding specific element.
    """

    def __init__(self, tree):
        """
        init with page source JSON data.json.

        tree = page source data.json
        """
        self.hierarchy_tree = {}
        # counter for found target string.
        self.count = -1
        if isinstance(tree, dict):
            self.hierarchy_tree = tree
        else:
            self.hierarchy_tree = json.loads(tree)
        # android process
        if "hierarchy" in self.hierarchy_tree:
            self.hierarchy_tree = self.hierarchy_tree['hierarchy']['node']
        self.init_with_json_data(self.hierarchy_tree)

        self.leaf_nodes_path = []
        self.available_nodes_path = []

    def init_with_json_data(self, tree, showInvisible=False, showDisabled=False):
        if "enabled" in tree:
            "iOS Node"
            tree['platform'] = 'iOS'
            for sub_tree in tree['children']:
                self.init_with_json_data(sub_tree, showInvisible, showDisabled)
        else:
            "Android Node"
            keys = [k for k in tree.keys() if k.startswith('@')]
            tree['platform'] = 'Android'
            for k, v in translate_map_android.items():
                if v in tree:
                    tree[k] = tree[v]
                    if tree[k] in ['true', 'false']:
                        tree[k] = True if tree[k] == 'true' else False

            ds = re.findall(r"\d+", tree['rect'])
            rect = {
                        "origin": {
                            "x": int(ds[0]),
                            "y": int(ds[1])
                        },
                        "size": {
                            "width": int(ds[2]) - int(ds[0]),
                            "height": int(ds[3]) - int(ds[1])
                        }
                    }
            tree['rect'] = rect

            if tree['@password'] == 'true':
                # password type textbox hides the text.
                tree['text'] = 'password,pwd,pass'
            for k in keys:
                if k in tree:
                    del(tree[k])

            if 'node' not in tree:
                # leaf node
                tree['children'] = []
                return True

            if isinstance(tree['node'], list):
                tree['children'] = copy.deepcopy(tree['node'])
            else:
                tree['children'] = [copy.deepcopy(tree['node'])]

            del(tree['node'])
            for sub_tree in tree['children']:
                self.init_with_json_data(sub_tree, showInvisible, showDisabled)

    def find_node_by_partial_text(self, text, count=1, tree=None):
        """
        DFS the matching node with explicit text.
        return the list of nodes from root node down to the selected node.
        you can get the node information by picking the [-1] of the returned array.
        """
        if not tree:
            tree = self.hierarchy_tree
        if self.count < 0:
            self.count = count

        "combine all strings in the node together. lowercase"
        strings = [s.encode('ascii', 'ignore') for s in tree.values() if isinstance(s, (str, unicode))]
        ss = ','.join(strings).lower()
        _text = [text] if isinstance(text, str) else text
        found = True
        for s in _text:
            if s.lower() not in ss:
                found = False
                break
        if found:
            self.count -= 1
            if self.count <= 0:
                self.count = -1
                return [tree]

        if not tree['children']:
            return []
        else:
            for child in tree['children']:
                nodes = self.find_node_by_partial_text(text, count, child)
                if nodes:
                    nodes.append(tree)
                    return nodes

    def find_all_available_elements(self, tree=None):
        """
        DFS iterate the tree and find out all elements meeting requirements.
        """
        if not tree:
            tree = self.hierarchy_tree

        if tree['visible'] and tree['enabled']:
            l = len(self.available_nodes_path) - 1
            temp = copy.deepcopy(self.available_nodes_path[l])
            self.available_nodes_path[l].append(tree)
            self.available_nodes_path[l].reverse()
            self.available_nodes_path.append(temp)

        self.available_nodes_path[len(self.available_nodes_path) - 1].append(tree)
        for child in tree['children']:
            self.find_all_available_elements(child)
        self.available_nodes_path[len(self.available_nodes_path) - 1].pop()

    def get_all_available_elements(self):
        self.available_nodes_path = [[]]
        self.find_all_available_elements()
        self.available_nodes_path.pop()
        anodes = []
        for nodes in self.available_nodes_path:
            xpath = self.get_xpath_for_selected_node(nodes)
            anodes.append(nodes[0])
            anodes[len(anodes)-1]['xpath'] = xpath
        return anodes

    def get_xpath_for_selected_node(self, nodes):
        """
        Generate the xPath for the selected node.
        the parameter is the nodes array from root node down to the selected one.
        """
        xpath = '/'
        i = len(nodes) - 2  # strip out the application node
        while i >= 0:
            parent = nodes[i+1]
            current = nodes[i]
            index = 0
            for child in parent['children']:
                if child['type'] == current['type']:
                    index += 1
                if child == current:
                    break
            xpath = ''.join([xpath, '/', short_type(current), '[', str(index), ']'])
            i -= 1
        return xpath

    def find_all_leaf_nodes(self, tree=None):
        """
        DFS all leaf nodes
        """
        if not tree:
            tree = self.hierarchy_tree
        if not tree['children']:
            l = len(self.leaf_nodes_path)
            temp = copy.deepcopy(self.leaf_nodes_path[l - 1])
            self.leaf_nodes_path[l - 1].append(tree)
            self.leaf_nodes_path[l - 1].reverse()
            self.leaf_nodes_path.append(temp)
            return True
        else:
            self.leaf_nodes_path[len(self.leaf_nodes_path) - 1].append(tree)
            for child in tree['children']:
                self.find_all_leaf_nodes(child)
            self.leaf_nodes_path[len(self.leaf_nodes_path) - 1].pop()

    def get_all_leaf_nodes(self):
        self.leaf_nodes_path = [[]]
        self.find_all_leaf_nodes()
        self.leaf_nodes_path.pop()
        leafs = []
        for nodes in self.leaf_nodes_path:
            xpath = self.get_xpath_for_selected_node(nodes)
            leafs.append(nodes[0])
            leafs[len(leafs)-1]['xpath'] = xpath
        return leafs


def short_type(node):
    """
    Return the short type name of node's type.
    """
    translate = {
        'iOS': {
            "UIASearchBar": "searchbar",
            "UIASecureTextField": "secure",
            "UIAPopover": "popover",
            "UIAElement": "element",
            "UIATabBar": "tabbar",
            "UIAActivityIndicator": "activityIndicator",
            "UIALink": "link",
            "UIAProgressIndicator": "progress",
            "UIASwitch": "switch",
            "UIAStatusBar": "statusbar",
            "UIASlider": "slider",
            "UIATextField": "textfield",
            "UIATableCell": "cell",
            "UIAWebView": "webview",
            "UIAImage": "image",
            "UIAStaticText": "text",
            "UIAToolbar": "toolbar",
            "UIAPicker": "picker",
            "UIAActionSheet": "actionsheet",
            "UIAButton": "button",
            "UIATableView": "tableview",
            "UIAPickerWheel": "pickerwheel",
            "UIAAlert": "alert",
            "UIAWindow": "window",
            "UIATableGroup": "group",
            "UIAScrollView": "scrollview",
            "UIAPageIndicator": "pageIndicator",
            "UIANavigationBar": "navigationBar",
            "UIATextView": "textview",
            "UIASegmentedControl": "segmented"
        },
        'Android': {
            "DatePicker": "datepicker",
            "DialerFilter": "dialerfilter",
            "AdapterViewFlipper": "adapterviewflipper",
            "CheckBox": "checkbox",
            "RelativeLayout": "relative",
            "ViewSwitcher": "viewswitcher",
            "Space": "space",
            "AbsListView": "abslist",
            "EditText": "textfield",
            "RSSurfaceView": "rssurface",
            "SearchView": "search",
            "PageTitleStrip": "pagetitlestrip",
            "Spinner": "spinner",
            "AdapterViewAnimator": "adapterviewanimator",
            "MediaController": "media",
            "RadioGroup": "radiogroup",
            "AbsSeekBar": "absseek",
            "FrameLayout": "window",
            "GridLayout": "gridlayout",
            "ZoomButton": "zoom",
            "ImageSwitcher": "imageswitcher",
            "AdapterView": "adapterview",
            "CalendarView": "calendar",
            "SurfaceView": "surface",
            "MultiAutoCompleteTextView": "multiautocomplete",
            "AnalogClock": "analogclock",
            "SeekBar": "seek",
            "StackView": "stack",
            "KeyboardView": "keyboard",
            "TableRow": "row",
            "LinearLayout": "linear",
            "ViewFlipper": "viewflipper",
            "ViewStub": "viewstub",
            "ZoomControls": "zoomcontrols",
            "ToggleButton": "toggle",
            "ExtractEditText": "extract",
            "ViewPager": "viewpager",
            "WebView": "web",
            "NumberPicker": "numberpicker",
            "ListView": "list",
            "FragmentTabHost": "fragmenttabhost",
            "Gallery": "gallery",
            "DigitalClock": "digitalclock",
            "TableLayout": "table",
            "TabWidget": "tabwidget",
            "PageTabStrip": "pagetabstrip",
            "GridView": "grid",
            "TwoLineListItem": "twolinelistitem",
            "AutoCompleteTextView": "autocomplete",
            "ViewGroup": "viewgroup",
            "TextClock": "textclock",
            "ViewAnimator": "viewanimator",
            "Button": "button",
            "Switch": "switch",
            "ScrollView": "scroll",
            "GLSurfaceView": "glsurface",
            "FragmentBreadCrumbs": "breadcrumbs",
            "RadioButton": "radio",
            "Chronometer": "chronometer",
            "RSTextureView": "rstexture",
            "ImageView": "image",
            "android.views.View": "views",
            "CompoundButton": "compound",
            "CheckedTextView": "checked",
            "MediaRouteButton": "mediaroutebutton",
            "HorizontalScrollView": "horizontal",
            "VideoView": "video",
            "TextureView": "texture",
            "ImageButton": "imagebutton",
            "QuickContactBadge": "quickcontactbadge",
            "AbsSpinner": "absspinner",
            "GestureOverlayView": "gesture",
            "ProgressBar": "progress",
            "ExpandableListView": "expandable",
            "TimePicker": "timepicker",
            "TextView": "text",
            "RatingBar": "rating",
            "SlidingDrawer": "drawer",
            "AppWidgetHostView": "appwidgethost",
            "AbsoluteLayout": "absolute",
            "TextSwitcher": "textswitcher",
            "TabHost": "tabhost"
        }

    }

    t = node['type']
    if "android.widget." in t:
        t = t.split('.')[-1]
    if t in translate[node['platform']]:
        return translate[node['platform']][t]
    else:
        return t


if __name__ == "__main__":

    f = open('../pagesource_original.txt')
    tmp = f.read()
    f.close()
    tmp = json.loads(tmp)
    t = PageSourceElementsTree(tmp)
    print json.dumps(t.get_all_available_elements())