import yfinance as yf
from langchain_core.tools import tool
from loguru import logger

# Dictionary mapping sectors to their industries for reference
SECTORS_AND_INDUSTRIES = {
    "basic-materials": [
        "agricultural-inputs",
        "aluminum",
        "building-materials",
        "chemicals",
        "coking-coal",
        "copper",
        "gold",
        "lumber-wood-production",
        "other-industrial-metals-mining",
        "other-precious-metals-mining",
        "paper-paper-products",
        "silver",
        "specialty-chemicals",
        "steel",
    ],
    "communication-services": [
        "advertising-agencies",
        "broadcasting",
        "electronic-gaming-multimedia",
        "entertainment",
        "internet-content-information",
        "publishing",
        "telecom-services",
    ],
    "consumer-cyclical": [
        "apparel-manufacturing",
        "apparel-retail",
        "auto-manufacturers",
        "auto-parts",
        "auto-truck-dealerships",
        "department-stores",
        "footwear-accessories",
        "furnishings-fixtures-appliances",
        "gambling",
        "home-improvement-retail",
        "internet-retail",
        "leisure",
        "lodging",
        "luxury-goods",
        "packaging-containers",
        "personal-services",
        "recreational-vehicles",
        "residential-construction",
        "resorts-casinos",
        "restaurants",
        "specialty-retail",
        "textile-manufacturing",
        "travel-services",
    ],
    "consumer-defensive": [
        "beverages-brewers",
        "beverages-non-alcoholic",
        "beverages-wineries-distilleries",
        "confectioners",
        "discount-stores",
        "education-training-services",
        "farm-products",
        "food-distribution",
        "grocery-stores",
        "household-personal-products",
        "packaged-foods",
        "tobacco",
    ],
    "energy": [
        "oil-gas-drilling",
        "oil-gas-e-p",
        "oil-gas-equipment-services",
        "oil-gas-integrated",
        "oil-gas-midstream",
        "oil-gas-refining-marketing",
        "thermal-coal",
        "uranium",
    ],
    "financial-services": [
        "asset-management",
        "banks-diversified",
        "banks-regional",
        "capital-markets",
        "credit-services",
        "financial-conglomerates",
        "financial-data-stock-exchanges",
        "insurance-brokers",
        "insurance-diversified",
        "insurance-life",
        "insurance-property-casualty",
        "insurance-reinsurance",
        "insurance-specialty",
        "mortgage-finance",
        "shell-companies",
    ],
    "healthcare": [
        "biotechnology",
        "diagnostics-research",
        "drug-manufacturers-general",
        "drug-manufacturers-specialty-generic",
        "health-information-services",
        "healthcare-plans",
        "medical-care-facilities",
        "medical-devices",
        "medical-distribution",
        "medical-instruments-supplies",
        "pharmaceutical-retailers",
    ],
    "industrials": [
        "aerospace-defense",
        "airlines",
        "airports-air-services",
        "building-products-equipment",
        "business-equipment-supplies",
        "conglomerates",
        "consulting-services",
        "electrical-equipment-parts",
        "engineering-construction",
        "farm-heavy-construction-machinery",
        "industrial-distribution",
        "infrastructure-operations",
        "integrated-freight-logistics",
        "marine-shipping",
        "metal-fabrication",
        "pollution-treatment-controls",
        "railroads",
        "rental-leasing-services",
        "security-protection-services",
        "specialty-business-services",
        "specialty-industrial-machinery",
        "staffing-employment-services",
        "tools-accessories",
        "trucking",
        "waste-management",
    ],
    "real-estate": [
        "real-estate-development",
        "real-estate-diversified",
        "real-estate-services",
        "reit-diversified",
        "reit-healthcare-facilities",
        "reit-hotel-motel",
        "reit-industrial",
        "reit-mortgage",
        "reit-office",
        "reit-residential",
        "reit-retail",
        "reit-specialty",
    ],
    "technology": [
        "communication-equipment",
        "computer-hardware",
        "consumer-electronics",
        "electronic-components",
        "electronics-computer-distribution",
        "information-technology-services",
        "scientific-technical-instruments",
        "semiconductor-equipment-materials",
        "semiconductors",
        "software-application",
        "software-infrastructure",
        "solar",
    ],
    "utilities": [
        "utilities-diversified",
        "utilities-independent-power-producers",
        "utilities-regulated-electric",
        "utilities-regulated-gas",
        "utilities-regulated-water",
        "utilities-renewable",
    ],
}


@tool(parse_docstring=True)
def get_sector_industries(sector_key: str):
    """
    Gets the industries within a financial market sector.

    Args:
        sector_key (str): The key representing the sector.
                          Valid sector keys include: basic-materials, communication-services,
                          consumer-cyclical, consumer-defensive, energy, financial-services,
                          healthcare, industrials, real-estate, technology, utilities.

    Returns:
        A DataFrame with industries' key, name, symbol, and market weight.

    Available Sectors and Industries:
    - basic-materials: agricultural-inputs, aluminum, building-materials, chemicals,
      coking-coal, copper, gold, lumber-wood-production, other-industrial-metals-mining,
      other-precious-metals-mining, paper-paper-products, silver, specialty-chemicals, steel
    - communication-services: advertising-agencies, broadcasting, electronic-gaming-multimedia,
      entertainment, internet-content-information, publishing, telecom-services
    - consumer-cyclical: apparel-manufacturing, apparel-retail, auto-manufacturers, auto-parts,
      auto-truck-dealerships, department-stores, footwear-accessories,
      furnishings-fixtures-appliances, gambling, home-improvement-retail, internet-retail,
      leisure, lodging, luxury-goods, packaging-containers, personal-services,
      recreational-vehicles, residential-construction, resorts-casinos, restaurants,
      specialty-retail, textile-manufacturing, travel-services
    - consumer-defensive: beverages-brewers, beverages-non-alcoholic,
      beverages-wineries-distilleries, confectioners, discount-stores,
      education-training-services, farm-products, food-distribution, grocery-stores,
      household-personal-products, packaged-foods, tobacco
    - energy: oil-gas-drilling, oil-gas-e-p, oil-gas-equipment-services, oil-gas-integrated,
      oil-gas-midstream, oil-gas-refining-marketing, thermal-coal, uranium
    - financial-services: asset-management, banks-diversified, banks-regional, capital-markets,
      credit-services, financial-conglomerates, financial-data-stock-exchanges,
      insurance-brokers, insurance-diversified, insurance-life, insurance-property-casualty,
      insurance-reinsurance, insurance-specialty, mortgage-finance, shell-companies
    - healthcare: biotechnology, diagnostics-research, drug-manufacturers-general,
      drug-manufacturers-specialty-generic, health-information-services, healthcare-plans,
      medical-care-facilities, medical-devices, medical-distribution,
      medical-instruments-supplies, pharmaceutical-retailers
    - industrials: aerospace-defense, airlines, airports-air-services,
      building-products-equipment, business-equipment-supplies, conglomerates,
      consulting-services, electrical-equipment-parts, engineering-construction,
      farm-heavy-construction-machinery, industrial-distribution, infrastructure-operations,
      integrated-freight-logistics, marine-shipping, metal-fabrication,
      pollution-treatment-controls, railroads, rental-leasing-services,
      security-protection-services, specialty-business-services,
      specialty-industrial-machinery, staffing-employment-services, tools-accessories,
      trucking, waste-management
    - real-estate: real-estate-development, real-estate-diversified, real-estate-services,
      reit-diversified, reit-healthcare-facilities, reit-hotel-motel, reit-industrial,
      reit-mortgage, reit-office, reit-residential, reit-retail, reit-specialty
    - technology: communication-equipment, computer-hardware, consumer-electronics,
      electronic-components, electronics-computer-distribution, information-technology-services,
      scientific-technical-instruments, semiconductor-equipment-materials, semiconductors,
      software-application, software-infrastructure, solar
    - utilities: utilities-diversified, utilities-independent-power-producers,
      utilities-regulated-electric, utilities-regulated-gas, utilities-regulated-water,
      utilities-renewable
    """
    try:
        sector = yf.Sector(sector_key)
        return sector.industries.to_dict()
    except Exception as e:
        logger.error(f"Error getting sector industries: {e}")
        return {"error": str(e)}


@tool(parse_docstring=True)
def get_sector_key(sector_key: str):
    """
    Retrieves the key of the specified sector.

    Args:
        sector_key (str): The key representing the sector.
                          Valid sector keys include: basic-materials, communication-services,
                          consumer-cyclical, consumer-defensive, energy, financial-services,
                          healthcare, industrials, real-estate, technology, utilities.

    Returns:
        The unique key of the sector.
    """
    try:
        sector = yf.Sector(sector_key)
        return sector.key
    except Exception as e:
        logger.error(f"Error getting sector key: {e}")
        return {"error": str(e)}


@tool(parse_docstring=True)
def get_sector_name(sector_key: str):
    """
    Retrieves the name of the specified sector.

    Args:
        sector_key (str): The key representing the sector.
                          Valid sector keys include: basic-materials, communication-services,
                          consumer-cyclical, consumer-defensive, energy, financial-services,
                          healthcare, industrials, real-estate, technology, utilities.

    Returns:
        The name of the sector.
    """
    try:
        sector = yf.Sector(sector_key)
        return sector.name
    except Exception as e:
        logger.error(f"Error getting sector name: {e}")
        return {"error": str(e)}


@tool(parse_docstring=True)
def get_sector_overview(sector_key: str):
    """
    Retrieves the overview information of the specified sector.

    Args:
        sector_key (str): The key representing the sector.
                          Valid sector keys include: basic-materials, communication-services,
                          consumer-cyclical, consumer-defensive, energy, financial-services,
                          healthcare, industrials, real-estate, technology, utilities.

    Returns:
        A dictionary containing an overview of the sector.
    """
    try:
        sector = yf.Sector(sector_key)
        return sector.overview
    except Exception as e:
        logger.error(f"Error getting sector overview: {e}")
        return {"error": str(e)}


@tool(parse_docstring=True)
def get_sector_research_reports(sector_key: str):
    """
    Retrieves research reports related to the specified sector.

    Args:
        sector_key (str): The key representing the sector.
                          Valid sector keys include: basic-materials, communication-services,
                          consumer-cyclical, consumer-defensive, energy, financial-services,
                          healthcare, industrials, real-estate, technology, utilities.

    Returns:
        A list of research reports, where each report is a dictionary with metadata.
    """
    try:
        sector = yf.Sector(sector_key)
        return sector.research_reports
    except Exception as e:
        logger.error(f"Error getting sector research reports: {e}")
        return {"error": str(e)}


@tool(parse_docstring=True)
def get_sector_symbol(sector_key: str):
    """
    Retrieves the symbol of the specified sector.

    Args:
        sector_key (str): The key representing the sector.
                          Valid sector keys include: basic-materials, communication-services,
                          consumer-cyclical, consumer-defensive, energy, financial-services,
                          healthcare, industrials, real-estate, technology, utilities.

    Returns:
        The symbol representing the sector.
    """
    try:
        sector = yf.Sector(sector_key)
        return sector.symbol
    except Exception as e:
        logger.error(f"Error getting sector symbol: {e}")
        return {"error": str(e)}


@tool(parse_docstring=True)
def get_sector_ticker(sector_key: str):
    """
    Retrieves a Ticker object based on the sector's symbol.

    Args:
        sector_key (str): The key representing the sector.
                          Valid sector keys include: basic-materials, communication-services,
                          consumer-cyclical, consumer-defensive, energy, financial-services,
                          healthcare, industrials, real-estate, technology, utilities.

    Returns:
        Information from the Ticker object associated with the sector.
    """
    try:
        sector = yf.Sector(sector_key)
        ticker = sector.ticker
        # Return ticker info instead of ticker object for serialization
        return ticker.info
    except Exception as e:
        logger.error(f"Error getting sector ticker: {e}")
        return {"error": str(e)}


@tool(parse_docstring=True)
def get_sector_top_companies(sector_key: str):
    """
    Retrieves the top companies within the specified sector.

    Args:
        sector_key (str): The key representing the sector.
                          Valid sector keys include: basic-materials, communication-services,
                          consumer-cyclical, consumer-defensive, energy, financial-services,
                          healthcare, industrials, real-estate, technology, utilities.

    Returns:
        A dictionary containing the top companies in the sector.
    """
    try:
        sector = yf.Sector(sector_key)
        return sector.top_companies.to_dict()
    except Exception as e:
        logger.error(f"Error getting sector top companies: {e}")
        return {"error": str(e)}


@tool(parse_docstring=True)
def get_sector_top_etfs(sector_key: str):
    """
    Gets the top ETFs for the specified sector.

    Args:
        sector_key (str): The key representing the sector.
                          Valid sector keys include: basic-materials, communication-services,
                          consumer-cyclical, consumer-defensive, energy, financial-services,
                          healthcare, industrials, real-estate, technology, utilities.

    Returns:
        A dictionary of ETF symbols and names.
    """
    try:
        sector = yf.Sector(sector_key)
        return sector.top_etfs
    except Exception as e:
        logger.error(f"Error getting sector top ETFs: {e}")
        return {"error": str(e)}


@tool(parse_docstring=True)
def get_sector_top_mutual_funds(sector_key: str):
    """
    Gets the top mutual funds for the specified sector.

    Args:
        sector_key (str): The key representing the sector.
                          Valid sector keys include: basic-materials, communication-services,
                          consumer-cyclical, consumer-defensive, energy, financial-services,
                          healthcare, industrials, real-estate, technology, utilities.

    Returns:
        A dictionary of mutual fund symbols and names.
    """
    try:
        sector = yf.Sector(sector_key)
        return sector.top_mutual_funds
    except Exception as e:
        logger.error(f"Error getting sector top mutual funds: {e}")
        return {"error": str(e)}


@tool(parse_docstring=True)
def list_available_sectors():
    """
    Returns a list of all available sectors that can be used with the sector tools.

    Returns:
        A dictionary mapping sector keys to their respective industries.
    """
    return SECTORS_AND_INDUSTRIES


tools = [
    get_sector_industries,
    get_sector_key,
    get_sector_name,
    get_sector_overview,
    get_sector_research_reports,
    get_sector_symbol,
    get_sector_ticker,
    get_sector_top_companies,
    get_sector_top_etfs,
    get_sector_top_mutual_funds,
    list_available_sectors,
]
TOOL_DESCRIPTION = """
Handles queries about financial market sectors.
It provides insights on sector overviews, industries, research reports, and top companies, ETFs, and mutual funds.
"""
