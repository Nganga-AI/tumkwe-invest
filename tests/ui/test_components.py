from tumkwe_invest.ui.components import (
    Button,
    Card,
    Chart,
    SectionLayout,
    Tab,
    ToggleSwitch,
    Tooltip,
    UIComponent,
    create_metric_card,
    create_tooltip_with_info,
    create_view_mode_toggle,
)


class TestUIComponent:
    def test_init(self):
        component = UIComponent("test-id")
        assert component.component_id == "test-id"
        assert component.classes == []
        assert component.attributes == {}
        assert component.event_handlers == {}

        # Test auto-generated ID
        auto_component = UIComponent()
        assert auto_component.component_id.startswith("component_")

    def test_add_class(self):
        component = UIComponent("test-id")
        returned = component.add_class("test-class")

        assert "test-class" in component.classes
        assert len(component.classes) == 1
        assert returned is component  # Test method chaining

        # Test duplicate classes aren't added
        component.add_class("test-class")
        assert len(component.classes) == 1

    def test_set_attribute(self):
        component = UIComponent("test-id")
        returned = component.set_attribute("data-test", "value")

        assert component.attributes["data-test"] == "value"
        assert returned is component  # Test method chaining

    def test_on_event(self):
        component = UIComponent("test-id")
        returned = component.on_event("click", "handleClick()")

        assert component.event_handlers["click"] == "handleClick()"
        assert returned is component  # Test method chaining

    def test_to_dict(self):
        component = UIComponent("test-id")
        component.add_class("test-class")
        component.set_attribute("data-test", "value")
        component.on_event("click", "handleClick()")

        result = component.to_dict()
        assert result["id"] == "test-id"
        assert "test-class" in result["classes"]
        assert result["attributes"]["data-test"] == "value"
        assert result["eventHandlers"]["click"] == "handleClick()"


class TestCard:
    def test_init(self):
        card = Card("Test Title", "Test Content", "card-id")
        assert card.component_id == "card-id"
        assert card.title == "Test Title"
        assert card.content == "Test Content"
        assert card.footer is None
        assert card.header_actions == []
        assert "card" in card.classes

    def test_set_content(self):
        card = Card("Test Title")
        returned = card.set_content({"key": "value"})

        assert card.content == {"key": "value"}
        assert returned is card  # Test method chaining

    def test_set_footer(self):
        card = Card("Test Title")
        returned = card.set_footer("Footer Text")

        assert card.footer == "Footer Text"
        assert returned is card

    def test_add_header_action(self):
        card = Card("Test Title")
        action = {"icon": "settings", "handler": "openSettings()"}
        returned = card.add_header_action(action)

        assert card.header_actions[0] == action
        assert returned is card

    def test_to_dict(self):
        card = Card("Test Title", "Test Content", "card-id")
        card.set_footer("Footer Text")
        card.add_header_action({"icon": "settings"})

        result = card.to_dict()
        assert result["type"] == "card"
        assert result["title"] == "Test Title"
        assert result["content"] == "Test Content"
        assert result["footer"] == "Footer Text"
        assert len(result["headerActions"]) == 1


class TestButton:
    def test_init(self):
        button = Button("Click Me", "danger", "large", "btn-id")
        assert button.component_id == "btn-id"
        assert button.label == "Click Me"
        assert button.icon is None
        assert button.disabled is False
        assert "button" in button.classes
        assert "button-danger" in button.classes
        assert "button-large" in button.classes

    def test_set_icon(self):
        button = Button("Click Me")
        returned = button.set_icon("arrow-right")

        assert button.icon == "arrow-right"
        assert returned is button

    def test_set_disabled(self):
        button = Button("Click Me")
        returned = button.set_disabled()

        assert button.disabled is True
        assert returned is button

        button.set_disabled(False)
        assert button.disabled is False

    def test_to_dict(self):
        button = Button("Click Me", "primary", "medium", "btn-id")
        button.set_icon("arrow-right")
        button.set_disabled(True)

        result = button.to_dict()
        assert result["type"] == "button"
        assert result["label"] == "Click Me"
        assert result["icon"] == "arrow-right"
        assert result["disabled"] is True


class TestTooltip:
    def test_init(self):
        tooltip = Tooltip("Help text", "left", "tip-id")
        assert tooltip.component_id == "tip-id"
        assert tooltip.content == "Help text"
        assert tooltip.position == "left"
        assert "tooltip" in tooltip.classes
        assert "tooltip-left" in tooltip.classes

    def test_set_content(self):
        tooltip = Tooltip("Help text")
        returned = tooltip.set_content("New help text")

        assert tooltip.content == "New help text"
        assert returned is tooltip

    def test_set_position(self):
        tooltip = Tooltip("Help text", "top")
        assert "tooltip-top" in tooltip.classes

        returned = tooltip.set_position("bottom")
        assert "tooltip-top" not in tooltip.classes
        assert "tooltip-bottom" in tooltip.classes
        assert tooltip.position == "bottom"
        assert returned is tooltip

    def test_to_dict(self):
        tooltip = Tooltip("Help text", "right", "tip-id")
        result = tooltip.to_dict()

        assert result["type"] == "tooltip"
        assert result["content"] == "Help text"
        assert result["position"] == "right"


class TestTab:
    def test_init(self):
        tabs = [
            {"label": "Tab 1", "content": "Content 1"},
            {"label": "Tab 2", "content": "Content 2"},
        ]
        tab = Tab(tabs, 1, "tabs-id")

        assert tab.component_id == "tabs-id"
        assert tab.tabs == tabs
        assert tab.active_tab == 1
        assert "tabs" in tab.classes

    def test_add_tab(self):
        tab = Tab([])
        returned = tab.add_tab("New Tab", "New Content")

        assert len(tab.tabs) == 1
        assert tab.tabs[0]["label"] == "New Tab"
        assert tab.tabs[0]["content"] == "New Content"
        assert returned is tab

    def test_set_active_tab(self):
        tabs = [
            {"label": "Tab 1", "content": "Content 1"},
            {"label": "Tab 2", "content": "Content 2"},
        ]
        tab = Tab(tabs, 0, "tabs-id")

        returned = tab.set_active_tab(1)
        assert tab.active_tab == 1
        assert returned is tab

        # Test invalid index
        tab.set_active_tab(99)
        assert tab.active_tab == 1  # Should not change

    def test_to_dict(self):
        tabs = [
            {"label": "Tab 1", "content": "Content 1"},
            {"label": "Tab 2", "content": "Content 2"},
        ]
        tab = Tab(tabs, 0, "tabs-id")

        result = tab.to_dict()
        assert result["type"] == "tabs"
        assert result["tabs"] == tabs
        assert result["activeTab"] == 0


class TestToggleSwitch:
    def test_init(self):
        toggle = ToggleSwitch("Enable Feature", True, "toggle-id")

        assert toggle.component_id == "toggle-id"
        assert toggle.label == "Enable Feature"
        assert toggle.checked is True
        assert toggle.description is None
        assert "toggle-switch" in toggle.classes

    def test_set_checked(self):
        toggle = ToggleSwitch("Enable Feature", True)

        returned = toggle.set_checked(False)
        assert toggle.checked is False
        assert returned is toggle

    def test_set_description(self):
        toggle = ToggleSwitch("Enable Feature")

        returned = toggle.set_description("This enables the feature")
        assert toggle.description == "This enables the feature"
        assert returned is toggle

    def test_to_dict(self):
        toggle = ToggleSwitch("Enable Feature", True, "toggle-id")
        toggle.set_description("This enables the feature")

        result = toggle.to_dict()
        assert result["type"] == "toggleSwitch"
        assert result["label"] == "Enable Feature"
        assert result["checked"] is True
        assert result["description"] == "This enables the feature"


class TestChart:
    def test_init(self):
        chart_config = {"title": "Sales Data", "type": "line"}
        chart = Chart(chart_config, "400px", "80%", "chart-id")

        assert chart.component_id == "chart-id"
        assert chart.chart_config == chart_config
        assert chart.height == "400px"
        assert chart.width == "80%"
        assert chart.title == "Sales Data"
        assert "chart" in chart.classes

    def test_set_height(self):
        chart_config = {"title": "Test Chart"}
        chart = Chart(chart_config)

        returned = chart.set_height("500px")
        assert chart.height == "500px"
        assert returned is chart

    def test_set_width(self):
        chart_config = {"title": "Test Chart"}
        chart = Chart(chart_config)

        returned = chart.set_width("90%")
        assert chart.width == "90%"
        assert returned is chart

    def test_update_config(self):
        chart_config = {"title": "Test Chart", "type": "bar"}
        chart = Chart(chart_config)

        returned = chart.update_config({"type": "line", "legend": True})
        assert chart.chart_config["type"] == "line"
        assert chart.chart_config["legend"] is True
        assert chart.chart_config["title"] == "Test Chart"  # Original value preserved
        assert returned is chart

    def test_to_dict(self):
        chart_config = {"title": "Test Chart", "type": "bar"}
        chart = Chart(chart_config, "400px", "100%", "chart-id")

        result = chart.to_dict()
        assert result["type"] == "chart"
        assert result["chartConfig"] == chart_config
        assert result["height"] == "400px"
        assert result["width"] == "100%"


class TestSectionLayout:
    def test_init(self):
        components = [{"type": "card", "config": {"title": "Test"}}]
        section = SectionLayout("My Section", components, True, "section-id")

        assert section.component_id == "section-id"
        assert section.title == "My Section"
        assert section.components == components
        assert section.collapsed is True
        assert section.description is None
        assert "section" in section.classes

    def test_add_component(self):
        section = SectionLayout("My Section")
        component = {"type": "button", "config": {"label": "Click"}}

        returned = section.add_component(component)
        assert len(section.components) == 1
        assert section.components[0] == component
        assert returned is section

    def test_set_description(self):
        section = SectionLayout("My Section")

        returned = section.set_description("Section description")
        assert section.description == "Section description"
        assert returned is section

    def test_set_collapsed(self):
        section = SectionLayout("My Section", collapsed=False)

        returned = section.set_collapsed(True)
        assert section.collapsed is True
        assert returned is section

    def test_to_dict(self):
        components = [{"type": "card", "config": {"title": "Test"}}]
        section = SectionLayout("My Section", components, True, "section-id")
        section.set_description("Section description")

        result = section.to_dict()
        assert result["type"] == "section"
        assert result["title"] == "My Section"
        assert result["components"] == components
        assert result["collapsed"] is True
        assert result["description"] == "Section description"


class TestHelperFunctions:
    def test_create_view_mode_toggle(self):
        toggle_basic = create_view_mode_toggle("basic")
        toggle_advanced = create_view_mode_toggle("advanced")

        assert toggle_basic["checked"] is False
        assert toggle_advanced["checked"] is True
        assert toggle_basic["id"] == "view-mode-toggle"
        assert "description" in toggle_basic
        assert "change" in toggle_basic["eventHandlers"]

    def test_create_tooltip_with_info(self):
        tooltip = create_tooltip_with_info("test-id", "Help information")

        assert tooltip["content"] == "Help information"
        assert tooltip["id"] == "test-id-tooltip"
        assert tooltip["attributes"]["data-target"] == "test-id"

    def test_create_metric_card(self):
        card = create_metric_card(
            "Revenue",
            "$1.5M",
            "Quarterly revenue",
            "+5%",
            "up",
            "Revenue increased by 5% compared to last quarter",
        )

        assert card["id"] == "metric-revenue"
        assert card["title"] == "Revenue"
        assert card["content"]["value"] == "$1.5M"
        assert card["content"]["description"] == "Quarterly revenue"
        assert card["content"]["trend"] == "+5%"
        assert card["content"]["trendDirection"] == "up"
        assert (
            card["attributes"]["data-tooltip"]
            == "Revenue increased by 5% compared to last quarter"
        )
        assert "metric-card" in card["classes"]

        # Test without optional parameters
        card_minimal = create_metric_card("Users", "10,000", "Active users")

        assert card_minimal["title"] == "Users"
        assert card_minimal["content"]["value"] == "10,000"
        assert "trend" not in card_minimal["content"]
        assert "trendDirection" not in card_minimal["content"]
