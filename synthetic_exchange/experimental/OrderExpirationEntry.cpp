#include "OrderExpirationEntry.h"
#include <iostream>

OrderExpirationEntry::OrderExpirationEntry() 
{
    tradingPair = "";
    orderId = "";
    timestamp = 0;
    expiration_timestamp = 0;
}

OrderExpirationEntry::OrderExpirationEntry(
	std::string tradingPair,
	std::string orderId,
	double timestamp,
	double expiration_timestamp) 
{
    tradingPair = tradingPair;
    orderId = orderId;
    timestamp = timestamp;
    expiration_timestamp = expiration_timestamp;
}

OrderExpirationEntry::OrderExpirationEntry(const OrderExpirationEntry &other)
{
    tradingPair = other.tradingPair;
    orderId = other.orderId;
    timestamp = other.timestamp;
    expiration_timestamp = other.expiration_timestamp;
}

OrderExpirationEntry &OrderExpirationEntry::operator=(const OrderExpirationEntry &other)
{
    tradingPair = other.tradingPair;
    orderId = other.orderId;
    timestamp = other.timestamp;
    expiration_timestamp = other.expiration_timestamp;
    return *this;
}

bool operator<(OrderExpirationEntry const &a, OrderExpirationEntry const &b) 
{
    if (a.expiration_timestamp == b.expiration_timestamp)
	{
        return a.orderId < b.orderId;
    }
    else
	{
        return a.expiration_timestamp < b.expiration_timestamp;
    }
}

std::string OrderExpirationEntry::getTradingPair() const 
{
    return tradingPair;
}

std::string OrderExpirationEntry::getClientOrderID() const 
{
    return orderId;
}

double OrderExpirationEntry::getTimestamp() const 
{
    return timestamp;
}

double OrderExpirationEntry::getExpirationTimestamp() const 
{
    return expiration_timestamp;
}
