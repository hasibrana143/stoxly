from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import logging

from services.search_service import smart_search, autocomplete, search_by_sector, search_by_market_cap
from stock_data_list import INDIAN_STOCKS_DATABASE

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/search", tags=["Search"])


@router.get("/")
async def search(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=100)):
    try:
        results = smart_search(q, INDIAN_STOCKS_DATABASE, limit=limit)
        return {"query": q, "count": len(results), "results": results}
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/autocomplete")
async def autocomplete_endpoint(q: str = Query(..., min_length=1), limit: int = Query(5, ge=1, le=20)):
    try:
        results = autocomplete(q, INDIAN_STOCKS_DATABASE, limit=limit)
        return {"query": q, "count": len(results), "results": results}
    except Exception as e:
        logger.error(f"Autocomplete error: {str(e)}")
        raise HTTPException(status_code=500, detail="Autocomplete failed")


@router.get("/by-sector/{sector}")
async def search_by_sector_endpoint(sector: str):
    try:
        results = search_by_sector(sector, INDIAN_STOCKS_DATABASE)
        return {"sector": sector, "count": len(results), "results": results}
    except Exception as e:
        logger.error(f"Sector search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Sector search failed")


@router.get("/by-cap/{category}")
async def search_by_cap_endpoint(category: str):
    try:
        valid_categories = {"large", "mid", "small"}
        if category.lower() not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {', '.join(sorted(valid_categories))}")
        results = search_by_market_cap(INDIAN_STOCKS_DATABASE, category)
        return {"category": category, "count": len(results), "results": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Market cap search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Market cap search failed")
