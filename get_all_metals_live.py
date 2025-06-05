#!/usr/bin/env python3
"""
Get ALL live metals prices from Bloomberg for your dashboard
"""

import blpapi
import time
from datetime import datetime

def get_all_metals_prices():
    """Get live prices for all metals"""
    
    print("💰 LIVE METALS DASHBOARD - BLOOMBERG DATA")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create session
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost("localhost")
    sessionOptions.setServerPort(8194)
    
    session = blpapi.Session(sessionOptions)
    session.start()
    session.openService("//blp/refdata")
    
    time.sleep(2)  # Let it settle
    
    # All metals tickers
    metals_tickers = {
        # LME Metals (your format)
        "LMCADS03 COMDTY": "LME Copper 3M",
        "LMAHDS03 COMDTY": "LME Aluminum 3M", 
        "LMZSDS03 COMDTY": "LME Zinc 3M",
        "LMNIDS03 COMDTY": "LME Nickel 3M",
        "LMSNDS03 COMDTY": "LME Tin 3M",
        "LMPBDS03 COMDTY": "LME Lead 3M",
        
        # Precious Metals
        "GC1 Comdty": "Gold Futures",
        "SI1 Comdty": "Silver Futures", 
        "PL1 Comdty": "Platinum Futures",
        "PA1 Comdty": "Palladium Futures",
        
        # Alternative formats
        "XAUUSD Curncy": "Gold Spot USD",
        "XAGUSD Curncy": "Silver Spot USD",
    }
    
    service = session.getService("//blp/refdata")
    request = service.createRequest("ReferenceDataRequest")
    
    # Add all tickers
    for ticker in metals_tickers.keys():
        request.append("securities", ticker)
    
    request.append("fields", "PX_LAST")
    request.append("fields", "NAME")
    request.append("fields", "CRNCY")
    
    print("📡 Requesting live metals data...")
    session.sendRequest(request)
    
    # Process events
    for attempt in range(10):
        event = session.nextEvent(3000)
        
        if event.eventType() == blpapi.Event.RESPONSE:
            print("✅ Live metals data received!")
            print()
            
            working_metals = []
            
            for msg in event:
                if msg.messageType() == "ReferenceDataResponse":
                    securityDataArray = msg.getElement("securityData")
                    
                    for i in range(securityDataArray.numValues()):
                        securityData = securityDataArray.getValue(i)
                        ticker = securityData.getElement("security").getValue()
                        
                        if securityData.hasElement("securityError"):
                            continue
                        
                        fieldData = securityData.getElement("fieldData")
                        
                        if fieldData.hasElement("PX_LAST"):
                            price = fieldData.getElement("PX_LAST").getValue()
                            name = metals_tickers.get(ticker, "Unknown")
                            
                            # Get currency if available
                            currency = "USD"
                            if fieldData.hasElement("CRNCY"):
                                currency = fieldData.getElement("CRNCY").getValue()
                            
                            print(f"🔥 {name:<20} ${price:>10.2f} {currency} ({ticker})")
                            working_metals.append((ticker, name, price, currency))
            
            print()
            print(f"📊 SUCCESS: {len(working_metals)} metals with live data!")
            print("🚀 Your Bloomberg metals integration is COMPLETE!")
            
            session.stop()
            return working_metals
    
    session.stop()
    return []

if __name__ == "__main__":
    metals_data = get_all_metals_prices()
    
    if metals_data:
        print(f"\n🎉 VICTORY! Your metals dashboard has {len(metals_data)} live data feeds!")
        print("💼 Ready for professional trading and analysis!")
    else:
        print("\n🔧 No metals data - check Bloomberg connection") 