"""
Reusable UI components for Tumkwe Invest.

This module provides reusable components for building user interfaces,
including cards, buttons, tooltips, and layout elements.
"""

from typing import Dict, List, Any, Optional, Union, Callable


class UIComponent:
    """Base class for all UI components."""
    
    def __init__(self, component_id: Optional[str] = None):
        """
        Initialize a UI component.
        
        Args:
            component_id: Optional component identifier
        """
        self.component_id = component_id or f"component_{id(self)}"
        self.classes = []
        self.attributes = {}
        self.event_handlers = {}
        
    def add_class(self, class_name: str) -> 'UIComponent':
        """Add a CSS class to the component."""
        if class_name not in self.classes:
            self.classes.append(class_name)
        return self
        
    def set_attribute(self, name: str, value: str) -> 'UIComponent':
        """Set an HTML attribute for the component."""
        self.attributes[name] = value
        return self
        
    def on_event(self, event_type: str, handler: str) -> 'UIComponent':
        """Register an event handler for the component."""
        self.event_handlers[event_type] = handler
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary representation."""
        return {
            "id": self.component_id,
            "classes": self.classes,
            "attributes": self.attributes,
            "eventHandlers": self.event_handlers
        }


class Card(UIComponent):
    """Card component for displaying content in a container."""
    
    def __init__(self, title: Optional[str] = None, 
                content: Optional[Union[str, Dict[str, Any]]] = None,
                component_id: Optional[str] = None):
        """
        Initialize a card component.
        
        Args:
            title: Optional card title
            content: Optional card content (string or dictionary)
            component_id: Optional component identifier
        """
        super().__init__(component_id)
        self.title = title
        self.content = content
        self.footer = None
        self.header_actions = []
        self.add_class("card")
    
    def set_title(self, title: str) -> 'Card':
        """Set the card title."""
        self.title = title
        return self
    
    def set_content(self, content: Union[str, Dict[str, Any]]) -> 'Card':
        """Set the card content."""
        self.content = content
        return self
    
    def set_footer(self, footer: str) -> 'Card':
        """Set the card footer content."""
        self.footer = footer
        return self
    
    def add_header_action(self, action: Dict[str, Any]) -> 'Card':
        """Add an action button to the card header."""
        self.header_actions.append(action)
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the card to a dictionary representation."""
        base_dict = super().to_dict()
        card_dict = {
            **base_dict,
            "type": "card",
            "title": self.title,
            "content": self.content,
            "footer": self.footer,
            "headerActions": self.header_actions
        }
        return card_dict


class Button(UIComponent):
    """Button component for user interactions."""
    
    def __init__(self, label: str, variant: str = "primary", 
                size: str = "medium", component_id: Optional[str] = None):
        """
        Initialize a button component.
        
        Args:
            label: Button text
            variant: Button style variant ('primary', 'secondary', 'danger', etc.)
            size: Button size ('small', 'medium', 'large')
            component_id: Optional component identifier
        """
        super().__init__(component_id)
        self.label = label
        self.icon = None
        self.disabled = False
        self.add_class("button")
        self.add_class(f"button-{variant}")
        self.add_class(f"button-{size}")
    
    def set_icon(self, icon: str) -> 'Button':
        """Set button icon."""
        self.icon = icon
        return self
    
    def set_disabled(self, disabled: bool = True) -> 'Button':
        """Set button disabled state."""
        self.disabled = disabled
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the button to a dictionary representation."""
        base_dict = super().to_dict()
        button_dict = {
            **base_dict,
            "type": "button",
            "label": self.label,
            "icon": self.icon,
            "disabled": self.disabled
        }
        return button_dict


class Tooltip(UIComponent):
    """Tooltip component for displaying additional information on hover."""
    
    def __init__(self, content: str, position: str = "top", 
                component_id: Optional[str] = None):
        """
        Initialize a tooltip component.
        
        Args:
            content: Tooltip content
            position: Tooltip position ('top', 'right', 'bottom', 'left')
            component_id: Optional component identifier
        """
        super().__init__(component_id)
        self.content = content
        self.position = position
        self.add_class("tooltip")
        self.add_class(f"tooltip-{position}")
    
    def set_content(self, content: str) -> 'Tooltip':
        """Set tooltip content."""
        self.content = content
        return self
    
    def set_position(self, position: str) -> 'Tooltip':
        """Set tooltip position."""
        self.remove_class(f"tooltip-{self.position}")
        self.position = position
        self.add_class(f"tooltip-{position}")
        return self
    
    def remove_class(self, class_name: str) -> 'Tooltip':
        """Remove a CSS class from the component."""
        if class_name in self.classes:
            self.classes.remove(class_name)
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tooltip to a dictionary representation."""
        base_dict = super().to_dict()
        tooltip_dict = {
            **base_dict,
            "type": "tooltip",
            "content": self.content,
            "position": self.position
        }
        return tooltip_dict


class Tab(UIComponent):
    """Tab component for organizing content into tabs."""
    
    def __init__(self, tabs: List[Dict[str, Any]], 
                default_tab: int = 0, component_id: Optional[str] = None):
        """
        Initialize a tab component.
        
        Args:
            tabs: List of tab configurations with label and content
            default_tab: Index of the default active tab
            component_id: Optional component identifier
        """
        super().__init__(component_id)
        self.tabs = tabs
        self.active_tab = default_tab
        self.add_class("tabs")
    
    def add_tab(self, label: str, content: Dict[str, Any]) -> 'Tab':
        """Add a tab to the component."""
        self.tabs.append({
            "label": label,
            "content": content
        })
        return self
    
    def set_active_tab(self, index: int) -> 'Tab':
        """Set the active tab."""
        if 0 <= index < len(self.tabs):
            self.active_tab = index
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tab to a dictionary representation."""
        base_dict = super().to_dict()
        tab_dict = {
            **base_dict,
            "type": "tabs",
            "tabs": self.tabs,
            "activeTab": self.active_tab
        }
        return tab_dict


class ToggleSwitch(UIComponent):
    """Toggle switch component for binary options."""
    
    def __init__(self, label: str, checked: bool = False, 
                component_id: Optional[str] = None):
        """
        Initialize a toggle switch component.
        
        Args:
            label: Label text
            checked: Initial state (True for on, False for off)
            component_id: Optional component identifier
        """
        super().__init__(component_id)
        self.label = label
        self.checked = checked
        self.description = None
        self.add_class("toggle-switch")
    
    def set_checked(self, checked: bool) -> 'ToggleSwitch':
        """Set the checked state."""
        self.checked = checked
        return self
    
    def set_description(self, description: str) -> 'ToggleSwitch':
        """Set an optional description text."""
        self.description = description
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the toggle switch to a dictionary representation."""
        base_dict = super().to_dict()
        toggle_dict = {
            **base_dict,
            "type": "toggleSwitch",
            "label": self.label,
            "checked": self.checked,
            "description": self.description
        }
        return toggle_dict


class Chart(UIComponent):
    """Chart component for data visualization."""
    
    def __init__(self, chart_config: Dict[str, Any],
                height: str = "300px", width: str = "100%",
                component_id: Optional[str] = None):
        """
        Initialize a chart component.
        
        Args:
            chart_config: Chart configuration object
            height: Chart height (CSS value)
            width: Chart width (CSS value)
            component_id: Optional component identifier
        """
        super().__init__(component_id)
        self.chart_config = chart_config
        self.height = height
        self.width = width
        self.title = chart_config.get("title", "")
        self.add_class("chart")
    
    def set_height(self, height: str) -> 'Chart':
        """Set chart height."""
        self.height = height
        return self
    
    def set_width(self, width: str) -> 'Chart':
        """Set chart width."""
        self.width = width
        return self
    
    def update_config(self, config_updates: Dict[str, Any]) -> 'Chart':
        """Update chart configuration with new values."""
        self.chart_config.update(config_updates)
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the chart to a dictionary representation."""
        base_dict = super().to_dict()
        chart_dict = {
            **base_dict,
            "type": "chart",
            "chartConfig": self.chart_config,
            "height": self.height,
            "width": self.width
        }
        return chart_dict


class SectionLayout(UIComponent):
    """Section layout component for organizing related content."""
    
    def __init__(self, title: str, components: List[Dict[str, Any]] = None,
                collapsed: bool = False, component_id: Optional[str] = None):
        """
        Initialize a section layout component.
        
        Args:
            title: Section title
            components: List of component configurations
            collapsed: Whether the section is initially collapsed
            component_id: Optional component identifier
        """
        super().__init__(component_id)
        self.title = title
        self.components = components or []
        self.collapsed = collapsed
        self.description = None
        self.add_class("section")
    
    def add_component(self, component: Dict[str, Any]) -> 'SectionLayout':
        """Add a component to the section."""
        self.components.append(component)
        return self
    
    def set_description(self, description: str) -> 'SectionLayout':
        """Set section description."""
        self.description = description
        return self
    
    def set_collapsed(self, collapsed: bool) -> 'SectionLayout':
        """Set whether the section is collapsed."""
        self.collapsed = collapsed
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the section layout to a dictionary representation."""
        base_dict = super().to_dict()
        section_dict = {
            **base_dict,
            "type": "section",
            "title": self.title,
            "description": self.description,
            "components": self.components,
            "collapsed": self.collapsed
        }
        return section_dict


def create_view_mode_toggle(current_mode: str = "basic") -> Dict[str, Any]:
    """
    Create a toggle switch for switching between basic and advanced views.
    
    Args:
        current_mode: Current view mode ('basic' or 'advanced')
    
    Returns:
        Toggle switch configuration
    """
    toggle = ToggleSwitch(
        label="Advanced View",
        checked=current_mode == "advanced",
        component_id="view-mode-toggle"
    )
    
    toggle.set_description("Switch between simplified and detailed analysis views")
    toggle.on_event("change", "toggleViewMode")
    
    return toggle.to_dict()


def create_tooltip_with_info(target_id: str, content: str) -> Dict[str, Any]:
    """
    Create a tooltip with information content.
    
    Args:
        target_id: ID of the element that triggers the tooltip
        content: Tooltip content
    
    Returns:
        Tooltip configuration
    """
    tooltip = Tooltip(
        content=content,
        position="top",
        component_id=f"{target_id}-tooltip"
    )
    
    tooltip.set_attribute("data-target", target_id)
    
    return tooltip.to_dict()


def create_metric_card(title: str, value: Any, description: str,
                      trend: Optional[str] = None, 
                      trend_direction: Optional[str] = None,
                      tooltip: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a card displaying a metric with optional trend and tooltip.
    
    Args:
        title: Metric title
        value: Metric value
        description: Short description
        trend: Optional trend text (e.g., '+15%')
        trend_direction: Direction ('up', 'down', 'neutral')
        tooltip: Optional detailed explanation
    
    Returns:
        Card configuration
    """
    card_id = f"metric-{title.lower().replace(' ', '-')}"
    
    card = Card(
        title=title,
        component_id=card_id
    )
    
    content = {
        "value": value,
        "description": description
    }
    
    if trend:
        content["trend"] = trend
        content["trendDirection"] = trend_direction or "neutral"
    
    card.set_content(content)
    card.add_class("metric-card")
    
    if tooltip:
        card.set_attribute("data-tooltip", tooltip)
    
    return card.to_dict()
