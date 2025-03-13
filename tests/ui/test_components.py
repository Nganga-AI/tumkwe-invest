"""Test cases for the components module."""

import unittest
from tumkwe_invest.ui.components import (
    UIComponent, Card, Button, Tooltip, Tab, ToggleSwitch, Chart, SectionLayout,
    create_view_mode_toggle, create_tooltip_with_info, create_metric_card
)


class TestUIComponent(unittest.TestCase):
    """Test the base UIComponent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.component = UIComponent(component_id="test-component")

    def test_initialization(self):
        """Test component initialization."""
        self.assertEqual(self.component.component_id, "test-component")
        self.assertEqual(self.component.classes, [])
        self.assertEqual(self.component.attributes, {})
        self.assertEqual(self.component.event_handlers, {})

    def test_add_class(self):
        """Test adding CSS class."""
        self.component.add_class("primary")
        self.component.add_class("large")
        
        self.assertIn("primary", self.component.classes)
        self.assertIn("large", self.component.classes)
        
        # Adding the same class twice should have no effect
        self.component.add_class("primary")
        self.assertEqual(self.component.classes.count("primary"), 1)
        
        # Test method chaining
        result = self.component.add_class("bold")
        self.assertIs(result, self.component)
        self.assertIn("bold", self.component.classes)

    def test_set_attribute(self):
        """Test setting HTML attribute."""
        self.component.set_attribute("data-test", "value")
        self.component.set_attribute("aria-label", "Test Component")
        
        self.assertEqual(self.component.attributes["data-test"], "value")
        self.assertEqual(self.component.attributes["aria-label"], "Test Component")
        
        # Test method chaining
        result = self.component.set_attribute("title", "Test Title")
        self.assertIs(result, self.component)
        self.assertEqual(self.component.attributes["title"], "Test Title")

    def test_on_event(self):
        """Test registering an event handler."""
        self.component.on_event("click", "handleClick()")
        self.component.on_event("mouseover", "handleMouseover()")
        
        self.assertEqual(self.component.event_handlers["click"], "handleClick()")
        self.assertEqual(self.component.event_handlers["mouseover"], "handleMouseover()")
        
        # Test method chaining
        result = self.component.on_event("keydown", "handleKeydown()")
        self.assertIs(result, self.component)
        self.assertEqual(self.component.event_handlers["keydown"], "handleKeydown()")

    def test_to_dict(self):
        """Test converting component to dictionary."""
        self.component.add_class("primary")
        self.component.set_attribute("data-test", "value")
        self.component.on_event("click", "handleClick()")
        
        component_dict = self.component.to_dict()
        
        self.assertEqual(component_dict["id"], "test-component")
        self.assertEqual(component_dict["classes"], ["primary"])
        self.assertEqual(component_dict["attributes"], {"data-test": "value"})
        self.assertEqual(component_dict["eventHandlers"], {"click": "handleClick()"})


class TestCard(unittest.TestCase):
    """Test the Card component."""

    def setUp(self):
        """Set up test fixtures."""
        self.card = Card(
            title="Test Card",
            content="Card content",
            component_id="test-card"
        )

    def test_initialization(self):
        """Test card initialization."""
        self.assertEqual(self.card.title, "Test Card")
        self.assertEqual(self.card.content, "Card content")
        self.assertEqual(self.card.component_id, "test-card")
        self.assertIsNone(self.card.footer)
        self.assertEqual(self.card.header_actions, [])
        self.assertIn("card", self.card.classes)

    def test_set_title(self):
        """Test setting card title."""
        self.card.set_title("Updated Title")
        self.assertEqual(self.card.title, "Updated Title")
        
        # Test method chaining
        result = self.card.set_title("New Title")
        self.assertIs(result, self.card)
        self.assertEqual(self.card.title, "New Title")

    def test_set_content(self):
        """Test setting card content."""
        # Test with string content
        self.card.set_content("New content")
        self.assertEqual(self.card.content, "New content")
        
        # Test with dictionary content
        content_dict = {"key1": "value1", "key2": "value2"}
        self.card.set_content(content_dict)
        self.assertEqual(self.card.content, content_dict)
        
        # Test method chaining
        result = self.card.set_content("Final content")
        self.assertIs(result, self.card)
        self.assertEqual(self.card.content, "Final content")

    def test_set_footer(self):
        """Test setting card footer."""
        self.card.set_footer("Card footer")
        self.assertEqual(self.card.footer, "Card footer")
        
        # Test method chaining
        result = self.card.set_footer("Updated footer")
        self.assertIs(result, self.card)
        self.assertEqual(self.card.footer, "Updated footer")

    def test_add_header_action(self):
        """Test adding header action."""
        action = {"icon": "edit", "label": "Edit", "handler": "editItem()"}
        self.card.add_header_action(action)
        
        self.assertEqual(len(self.card.header_actions), 1)
        self.assertEqual(self.card.header_actions[0], action)
        
        # Add another action
        action2 = {"icon": "delete", "label": "Delete", "handler": "deleteItem()"}
        result = self.card.add_header_action(action2)
        self.assertIs(result, self.card)
        self.assertEqual(len(self.card.header_actions), 2)
        self.assertEqual(self.card.header_actions[1], action2)

    def test_to_dict(self):
        """Test converting card to dictionary."""
        self.card.set_footer("Card footer")
        action = {"icon": "edit", "label": "Edit", "handler": "editItem()"}
        self.card.add_header_action(action)
        
        card_dict = self.card.to_dict()
        
        self.assertEqual(card_dict["type"], "card")
        self.assertEqual(card_dict["title"], "Test Card")
        self.assertEqual(card_dict["content"], "Card content")
        self.assertEqual(card_dict["footer"], "Card footer")
        self.assertEqual(card_dict["headerActions"], [action])


class TestButton(unittest.TestCase):
    """Test the Button component."""

    def setUp(self):
        """Set up test fixtures."""
        self.button = Button(
            label="Click Me",
            variant="primary",
            size="medium",
            component_id="test-button"
        )

    def test_initialization(self):
        """Test button initialization."""
        self.assertEqual(self.button.label, "Click Me")
        self.assertEqual(self.button.component_id, "test-button")
        self.assertIsNone(self.button.icon)
        self.assertFalse(self.button.disabled)
        self.assertIn("button", self.button.classes)
        self.assertIn("button-primary", self.button.classes)
        self.assertIn("button-medium", self.button.classes)

    def test_set_icon(self):
        """Test setting button icon."""
        self.button.set_icon("plus")
        self.assertEqual(self.button.icon, "plus")
        
        # Test method chaining
        result = self.button.set_icon("minus")
        self.assertIs(result, self.button)
        self.assertEqual(self.button.icon, "minus")

    def test_set_disabled(self):
        """Test setting disabled state."""
        self.assertFalse(self.button.disabled)
        
        self.button.set_disabled(True)
        self.assertTrue(self.button.disabled)
        
        # Test with default value
        self.button.set_disabled()
        self.assertTrue(self.button.disabled)
        
        # Test method chaining
        result = self.button.set_disabled(False)
        self.assertIs(result, self.button)
        self.assertFalse(self.button.disabled)

    def test_to_dict(self):
        """Test converting button to dictionary."""
        self.button.set_icon("check")
        self.button.set_disabled(True)
        
        button_dict = self.button.to_dict()
        
        self.assertEqual(button_dict["type"], "button")
        self.assertEqual(button_dict["label"], "Click Me")
        self.assertEqual(button_dict["icon"], "check")
        self.assertTrue(button_dict["disabled"])


class TestTooltip(unittest.TestCase):
    """Test the Tooltip component."""

    def setUp(self):
        """Set up test fixtures."""
        self.tooltip = Tooltip(
            content="This is a tooltip",
            position="top",
            component_id="test-tooltip"
        )

    def test_initialization(self):
        """Test tooltip initialization."""
        self.assertEqual(self.tooltip.content, "This is a tooltip")
        self.assertEqual(self.tooltip.position, "top")
        self.assertEqual(self.tooltip.component_id, "test-tooltip")
        self.assertIn("tooltip", self.tooltip.classes)
        self.assertIn("tooltip-top", self.tooltip.classes)

    def test_set_content(self):
        """Test setting tooltip content."""
        self.tooltip.set_content("Updated tooltip content")
        self.assertEqual(self.tooltip.content, "Updated tooltip content")
        
        # Test method chaining
        result = self.tooltip.set_content("Final content")
        self.assertIs(result, self.tooltip)
        self.assertEqual(self.tooltip.content, "Final content")

    def test_set_position(self):
        """Test setting tooltip position."""
        self.tooltip.set_position("bottom")
        self.assertEqual(self.tooltip.position, "bottom")
        self.assertIn("tooltip-bottom", self.tooltip.classes)
        self.assertNotIn("tooltip-top", self.tooltip.classes)
        
        # Test method chaining
        result = self.tooltip.set_position("left")
        self.assertIs(result, self.tooltip)
        self.assertEqual(self.tooltip.position, "left")
        self.assertIn("tooltip-left", self.tooltip.classes)
        self.assertNotIn("tooltip-bottom", self.tooltip.classes)

    def test_remove_class(self):
        """Test removing a CSS class."""
        self.tooltip.add_class("test-class")
        self.assertIn("test-class", self.tooltip.classes)
        
        self.tooltip.remove_class("test-class")
        self.assertNotIn("test-class", self.tooltip.classes)
        
        # Test method chaining
        result = self.tooltip.remove_class("non-existent")
        self.assertIs(result, self.tooltip)

    def test_to_dict(self):
        """Test converting tooltip to dictionary."""
        tooltip_dict = self.tooltip.to_dict()
        
        self.assertEqual(tooltip_dict["type"], "tooltip")
        self.assertEqual(tooltip_dict["content"], "This is a tooltip")
        self.assertEqual(tooltip_dict["position"], "top")


class TestTab(unittest.TestCase):
    """Test the Tab component."""

    def setUp(self):
        """Set up test fixtures."""
        self.tabs = [
            {"label": "Tab 1", "content": {"text": "Content 1"}},
            {"label": "Tab 2", "content": {"text": "Content 2"}}
        ]
        self.tab = Tab(
            tabs=self.tabs,
            default_tab=0,
            component_id="test-tab"
        )

    def test_initialization(self):
        """Test tab initialization."""
        self.assertEqual(self.tab.tabs, self.tabs)
        self.assertEqual(self.tab.active_tab, 0)
        self.assertEqual(self.tab.component_id, "test-tab")
        self.assertIn("tabs", self.tab.classes)

    def test_add_tab(self):
        """Test adding a tab."""
        new_tab = {"label": "Tab 3", "content": {"text": "Content 3"}}
        self.tab.add_tab("Tab 3", {"text": "Content 3"})
        
        self.assertEqual(len(self.tab.tabs), 3)
        self.assertEqual(self.tab.tabs[2]["label"], "Tab 3")
        self.assertEqual(self.tab.tabs[2]["content"]["text"], "Content 3")
        
        # Test method chaining
        result = self.tab.add_tab("Tab 4", {"text": "Content 4"})
        self.assertIs(result, self.tab)
        self.assertEqual(len(self.tab.tabs), 4)

    def test_set_active_tab(self):
        """Test setting active tab."""
        self.tab.set_active_tab(1)
        self.assertEqual(self.tab.active_tab, 1)
        
        # Test with invalid index (should not change)
        self.tab.set_active_tab(99)
        self.assertEqual(self.tab.active_tab, 1)
        
        # Test method chaining
        result = self.tab.set_active_tab(0)
        self.assertIs(result, self.tab)
        self.assertEqual(self.tab.active_tab, 0)

    def test_to_dict(self):
        """Test converting tab to dictionary."""
        tab_dict = self.tab.to_dict()
        
        self.assertEqual(tab_dict["type"], "tabs")
        self.assertEqual(tab_dict["tabs"], self.tabs)
        self.assertEqual(tab_dict["activeTab"], 0)


class TestToggleSwitch(unittest.TestCase):
    """Test the ToggleSwitch component."""

    def setUp(self):
        """Set up test fixtures."""
        self.toggle = ToggleSwitch(
            label="Enable Feature",
            checked=False,
            component_id="test-toggle"
        )

    def test_initialization(self):
        """Test toggle switch initialization."""
        self.assertEqual(self.toggle.label, "Enable Feature")
        self.assertFalse(self.toggle.checked)
        self.assertIsNone(self.toggle.description)
        self.assertEqual(self.toggle.component_id, "test-toggle")
        self.assertIn("toggle-switch", self.toggle.classes)

    def test_set_checked(self):
        """Test setting checked state."""
        self.toggle.set_checked(True)
        self.assertTrue(self.toggle.checked)
        
        # Test method chaining
        result = self.toggle.set_checked(False)
        self.assertIs(result, self.toggle)
        self.assertFalse(self.toggle.checked)

    def test_set_description(self):
        """Test setting description."""
        description = "This feature enables advanced functionality."
        self.toggle.set_description(description)
        self.assertEqual(self.toggle.description, description)
        
        # Test method chaining
        new_description = "Updated description"
        result = self.toggle.set_description(new_description)
        self.assertIs(result, self.toggle)
        self.assertEqual(self.toggle.description, new_description)

    def test_to_dict(self):
        """Test converting toggle switch to dictionary."""
        description = "This feature enables advanced functionality."
        self.toggle.set_description(description)
        self.toggle.set_checked(True)
        
        toggle_dict = self.toggle.to_dict()
        
        self.assertEqual(toggle_dict["type"], "toggleSwitch")
        self.assertEqual(toggle_dict["label"], "Enable Feature")
        self.assertTrue(toggle_dict["checked"])
        self.assertEqual(toggle_dict["description"], description)


class TestChart(unittest.TestCase):
    """Test the Chart component."""

    def setUp(self):
        """Set up test fixtures."""
        self.chart_config = {
            "type": "line",
            "data": {
                "labels": ["Jan", "Feb", "Mar"],
                "datasets": [{
                    "label": "Sales",
                    "data": [10, 20, 30]
                }]
            },
            "title": "Monthly Sales"
        }
        self.chart = Chart(
            chart_config=self.chart_config,
            height="400px",
            width="100%",
            component_id="test-chart"
        )

    def test_initialization(self):
        """Test chart initialization."""
        self.assertEqual(self.chart.chart_config, self.chart_config)
        self.assertEqual(self.chart.height, "400px")
        self.assertEqual(self.chart.width, "100%")
        self.assertEqual(self.chart.title, "Monthly Sales")
        self.assertEqual(self.chart.component_id, "test-chart")
        self.assertIn("chart", self.chart.classes)

    def test_set_height(self):
        """Test setting chart height."""
        self.chart.set_height("500px")
        self.assertEqual(self.chart.height, "500px")
        
        # Test method chaining
        result = self.chart.set_height("600px")
        self.assertIs(result, self.chart)
        self.assertEqual(self.chart.height, "600px")

    def test_set_width(self):
        """Test setting chart width."""
        self.chart.set_width("80%")
        self.assertEqual(self.chart.width, "80%")
        
        # Test method chaining
        result = self.chart.set_width("90%")
        self.assertIs(result, self.chart)
        self.assertEqual(self.chart.width, "90%")

    def test_update_config(self):
        """Test updating chart configuration."""
        updates = {
            "title": "Updated Title",
            "options": {"responsive": False}
        }
        self.chart.update_config(updates)
        
        self.assertEqual(self.chart.chart_config["title"], "Updated Title")
        self.assertEqual(self.chart.chart_config["options"]["responsive"], False)
        
        # Test method chaining
        result = self.chart.update_config({"title": "Final Title"})
        self.assertIs(result, self.chart)
        self.assertEqual(self.chart.chart_config["title"], "Final Title")

    def test_to_dict(self):
        """Test converting chart to dictionary."""
        chart_dict = self.chart.to_dict()
        
        self.assertEqual(chart_dict["type"], "chart")
        self.assertEqual(chart_dict["chartConfig"], self.chart_config)
        self.assertEqual(chart_dict["height"], "400px")
        self.assertEqual(chart_dict["width"], "100%")


class TestSectionLayout(unittest.TestCase):
    """Test the SectionLayout component."""

    def setUp(self):
        """Set up test fixtures."""
        self.components = [
            {"type": "card", "config": {"title": "Card 1"}},
            {"type": "button", "config": {"label": "Button 1"}}
        ]
        self.section = SectionLayout(
            title="Test Section",
            components=self.components,
            collapsed=False,
            component_id="test-section"
        )

    def test_initialization(self):
        """Test section layout initialization."""
        self.assertEqual(self.section.title, "Test Section")
        self.assertEqual(self.section.components, self.components)
        self.assertFalse(self.section.collapsed)
        self.assertIsNone(self.section.description)
        self.assertEqual(self.section.component_id, "test-section")
        self.assertIn("section", self.section.classes)

    def test_add_component(self):
        """Test adding a component to the section."""
        new_component = {"type": "chart", "config": {"type": "line"}}
        self.section.add_component(new_component)
        
        self.assertEqual(len(self.section.components), 3)
        self.assertEqual(self.section.components[2], new_component)
        
        # Test method chaining
        result = self.section.add_component({"type": "tooltip", "config": {}})
        self.assertIs(result, self.section)
        self.assertEqual(len(self.section.components), 4)

    def test_set_description(self):
        """Test setting section description."""
        description = "This section contains test components."
        self.section.set_description(description)
        self.assertEqual(self.section.description, description)
        
        # Test method chaining
        new_description = "Updated section description"
        result = self.section.set_description(new_description)
        self.assertIs(result, self.section)
        self.assertEqual(self.section.description, new_description)

    def test_set_collapsed(self):
        """Test setting collapsed state."""
        self.section.set_collapsed(True)
        self.assertTrue(self.section.collapsed)
        
        # Test method chaining
        result = self.section.set_collapsed(False)
        self.assertIs(result, self.section)
        self.assertFalse(self.section.collapsed)

    def test_to_dict(self):
        """Test converting section layout to dictionary."""
        description = "This section contains test components."
        self.section.set_description(description)
        
        section_dict = self.section.to_dict()
        
        self.assertEqual(section_dict["type"], "section")
        self.assertEqual(section_dict["title"], "Test Section")
        self.assertEqual(section_dict["description"], description)
        self.assertEqual(section_dict["components"], self.components)
        self.assertFalse(section_dict["collapsed"])


class TestHelperFunctions(unittest.TestCase):
    """Test the helper functions."""

    def test_create_view_mode_toggle(self):
        """Test creating a view mode toggle."""
        # Test with basic mode
        toggle = create_view_mode_toggle("basic")
        self.assertEqual(toggle["type"], "toggleSwitch")
        self.assertEqual(toggle["label"], "Advanced View")
        self.assertFalse(toggle["checked"])
        
        # Test with advanced mode
        toggle = create_view_mode_toggle("advanced")
        self.assertEqual(toggle["type"], "toggleSwitch")
        self.assertEqual(toggle["label"], "Advanced View")
        self.assertTrue(toggle["checked"])

    def test_create_tooltip_with_info(self):
        """Test creating an info tooltip."""
        tooltip = create_tooltip_with_info("test-target", "This is info content")
        
        self.assertEqual(tooltip["type"], "tooltip")
        self.assertEqual(tooltip["content"], "This is info content")
        self.assertEqual(tooltip["position"], "top")
        self.assertEqual(tooltip["id"], "test-target-tooltip")
        self.assertEqual(tooltip["attributes"]["data-target"], "test-target")

    def test_create_metric_card(self):
        """Test creating a metric card."""
        # Test with minimal parameters
        card = create_metric_card(
            title="Revenue",
            value="$1,000,000",
            description="Annual revenue"
        )
        
        self.assertEqual(card["type"], "card")
        self.assertEqual(card["title"], "Revenue")
        self.assertEqual(card["content"]["value"], "$1,000,000")
        self.assertEqual(card["content"]["description"], "Annual revenue")
        
        # Test with all parameters
        card = create_metric_card(
            title="Growth",
            value="15%",
            description="Year over year",
            trend="+5%",
            trend_direction="up",
            tooltip="Growth measures increase over time."
        )
        
        self.assertEqual(card["type"], "card")
        self.assertEqual(card["title"], "Growth")
        self.assertEqual(card["content"]["value"], "15%")
        self.assertEqual(card["content"]["description"], "Year over year")
        self.assertEqual(card["content"]["trend"], "+5%")
        self.assertEqual(card["content"]["trendDirection"], "up")
        self.assertEqual(card["attributes"]["data-tooltip"], "Growth measures increase over time.")


if __name__ == "__main__":
    unittest.main()
