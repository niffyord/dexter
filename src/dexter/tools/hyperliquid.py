"""Hyperliquid MCP tool wrappers exposed as LangChain tools."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain.tools import tool

# Ensure the hyperliquid-mcp package (bundled in this repo) is importable.
_HYPERLIQUID_SRC = Path(__file__).resolve().parents[2] / "hyperliquid-mcp" / "src"
if _HYPERLIQUID_SRC.exists():
    sys.path.insert(0, str(_HYPERLIQUID_SRC))

from hyperliquid_mcp.models import (  # type: ignore  # noqa: E402
    AssetFilterRequest,
    BulkCancelRequest,
    CalculateMinOrderSizeRequest,
    CancelOrderRequest,
    CandleInterval,
    GetCandleDataRequest,
    GetFundingRatesRequest,
    GetL2OrderbookRequest,
    GetMarketDataRequest,
    GetUserFillsRequest,
    ModifyOrderRequest,
    OrderStatusRequest,
    OrderType,
    PlaceOrderRequest,
    TimeInForce,
    UpdateLeverageRequest,
    UserAddressRequest,
    WithdrawRequest,
)
from hyperliquid_mcp.server import mcp  # type: ignore  # noqa: E402


def _invoke_mcp_tool(tool_name: str, request_model: Any) -> Dict[str, Any]:
    """Invoke an MCP tool synchronously and return its JSON response."""
    tool_entry = mcp._tool_manager._tools.get(tool_name)
    if tool_entry is None:
        raise ValueError(f"Hyperliquid MCP tool '{tool_name}' is not registered")

    async def _run() -> Dict[str, Any]:
        return await tool_entry.fn(request_model)

    try:
        return asyncio.run(_run())
    except RuntimeError as exc:
        raise RuntimeError(
            "Hyperliquid MCP tools must be invoked from a synchronous context"
        ) from exc


@tool(args_schema=UserAddressRequest)
def get_positions(user: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve the current perpetual futures positions and margin summary for a user."""
    request = UserAddressRequest(user=user)
    return _invoke_mcp_tool("get_positions", request)


@tool(args_schema=UserAddressRequest)
def get_spot_user_state(user: Optional[str] = None) -> Dict[str, Any]:
    """Fetch spot account balances and collateral information for a user."""
    request = UserAddressRequest(user=user)
    return _invoke_mcp_tool("get_spot_user_state", request)


@tool(args_schema=UserAddressRequest)
def get_user_fees(user: Optional[str] = None) -> Dict[str, Any]:
    """Return Hyperliquid fee tier information and recent volume for a user."""
    request = UserAddressRequest(user=user)
    return _invoke_mcp_tool("get_user_fees", request)


@tool(args_schema=GetMarketDataRequest)
def get_market_data(asset: str) -> Dict[str, Any]:
    """Pull the latest Hyperliquid market snapshot (price, open interest, etc.) for an asset."""
    request = GetMarketDataRequest(asset=asset)
    return _invoke_mcp_tool("get_market_data", request)


@tool(args_schema=CalculateMinOrderSizeRequest)
def calculate_min_order_size(asset: str, min_value_usd: float = 10.0) -> Dict[str, Any]:
    """Compute the minimum contract size needed to meet the exchange notional requirement."""
    request = CalculateMinOrderSizeRequest(asset=asset, min_value_usd=min_value_usd)
    return _invoke_mcp_tool("calculate_min_order_size", request)


@tool(args_schema=GetCandleDataRequest)
def get_candle_data(
    asset: str,
    interval: CandleInterval,
    start_time: int,
    end_time: int,
) -> Dict[str, Any]:
    """Retrieve OHLCV candles for an asset over a given time range."""
    request = GetCandleDataRequest(
        asset=asset,
        interval=interval,
        start_time=start_time,
        end_time=end_time,
    )
    return _invoke_mcp_tool("get_candle_data", request)


@tool(args_schema=GetFundingRatesRequest)
def get_funding_rates(
    asset: Optional[str] = None,
    include_history: bool = False,
    start_time: Optional[int] = None,
) -> Dict[str, Any]:
    """Fetch current (and optionally historical) perpetual funding rates."""
    request = GetFundingRatesRequest(
        asset=asset,
        include_history=include_history,
        start_time=start_time,
    )
    return _invoke_mcp_tool("get_funding_rates", request)


@tool(args_schema=GetL2OrderbookRequest)
def get_l2_orderbook(
    asset: str,
    significant_figures: Optional[int] = None,
) -> Dict[str, Any]:
    """Get aggregated Level-2 order book depth for an asset."""
    request = GetL2OrderbookRequest(
        asset=asset,
        significant_figures=significant_figures,
    )
    return _invoke_mcp_tool("get_l2_orderbook", request)


@tool(args_schema=PlaceOrderRequest)
def place_order(
    asset: str,
    is_buy: bool,
    size: float,
    order_type: OrderType = OrderType.MARKET,
    price: Optional[float] = None,
    time_in_force: TimeInForce = TimeInForce.GTC,
    reduce_only: bool = False,
    take_profit: Optional[float] = None,
    stop_loss: Optional[float] = None,
) -> Dict[str, Any]:
    """Submit a trading order on Hyperliquid (market, limit, or trigger)."""
    request = PlaceOrderRequest(
        asset=asset,
        is_buy=is_buy,
        size=size,
        order_type=order_type,
        price=price,
        time_in_force=time_in_force,
        reduce_only=reduce_only,
        take_profit=take_profit,
        stop_loss=stop_loss,
    )
    return _invoke_mcp_tool("place_order", request)


@tool(args_schema=CancelOrderRequest)
def cancel_order(asset: str, order_id: int) -> Dict[str, Any]:
    """Cancel a specific open order by ID."""
    request = CancelOrderRequest(asset=asset, order_id=order_id)
    return _invoke_mcp_tool("cancel_order", request)


@tool(args_schema=ModifyOrderRequest)
def modify_order(
    asset: str,
    order_id: int,
    new_price: Optional[float] = None,
    new_size: Optional[float] = None,
    new_time_in_force: Optional[TimeInForce] = None,
) -> Dict[str, Any]:
    """Modify price, size, or time-in-force for an existing order."""
    request = ModifyOrderRequest(
        asset=asset,
        order_id=order_id,
        new_price=new_price,
        new_size=new_size,
        new_time_in_force=new_time_in_force,
    )
    return _invoke_mcp_tool("modify_order", request)


@tool(args_schema=AssetFilterRequest)
def cancel_all_orders(asset: Optional[str] = None) -> Dict[str, Any]:
    """Cancel every open order, optionally scoped to a single asset."""
    request = AssetFilterRequest(asset=asset)
    return _invoke_mcp_tool("cancel_all_orders", request)


@tool(args_schema=BulkCancelRequest)
def bulk_cancel_orders(orders: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Cancel a batch of orders; each entry needs an asset symbol and order_id."""
    request = BulkCancelRequest(orders=orders)
    return _invoke_mcp_tool("bulk_cancel_orders", request)


@tool(args_schema=UserAddressRequest)
def get_open_orders(user: Optional[str] = None) -> Dict[str, Any]:
    """List all currently open orders for a trader."""
    request = UserAddressRequest(user=user)
    return _invoke_mcp_tool("get_open_orders", request)


@tool(args_schema=OrderStatusRequest)
def get_order_status(order_id: int, user: Optional[str] = None) -> Dict[str, Any]:
    """Check the latest status for a specific order."""
    request = OrderStatusRequest(order_id=order_id, user=user)
    return _invoke_mcp_tool("get_order_status", request)


@tool(args_schema=UserAddressRequest)
def get_user_fills(user: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve the most recent fills/executions for a trader."""
    request = UserAddressRequest(user=user)
    return _invoke_mcp_tool("get_user_fills", request)


@tool(args_schema=GetUserFillsRequest)
def get_user_fills_by_time(
    start_time: int,
    end_time: Optional[int] = None,
    user: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve fills for a trader constrained to a specific time window (epoch ms)."""
    request = GetUserFillsRequest(
        start_time=start_time,
        end_time=end_time,
        user=user,
    )
    return _invoke_mcp_tool("get_user_fills_by_time", request)


@tool(args_schema=UpdateLeverageRequest)
def update_leverage(asset: str, leverage: float, is_isolated: bool = True) -> Dict[str, Any]:
    """Adjust isolated or cross leverage settings for an asset."""
    request = UpdateLeverageRequest(
        asset=asset,
        leverage=leverage,
        is_isolated=is_isolated,
    )
    return _invoke_mcp_tool("update_leverage", request)


@tool(args_schema=WithdrawRequest)
def withdraw(destination: str, amount: float) -> Dict[str, Any]:
    """Initiate a USDC withdrawal to an external wallet (requires trading permissions)."""
    request = WithdrawRequest(destination=destination, amount=amount)
    return _invoke_mcp_tool("withdraw", request)


TOOLS = [
    get_positions,
    get_spot_user_state,
    get_user_fees,
    get_market_data,
    calculate_min_order_size,
    get_candle_data,
    get_funding_rates,
    get_l2_orderbook,
    place_order,
    cancel_order,
    modify_order,
    cancel_all_orders,
    bulk_cancel_orders,
    get_open_orders,
    get_order_status,
    get_user_fills,
    get_user_fills_by_time,
    update_leverage,
    withdraw,
]
