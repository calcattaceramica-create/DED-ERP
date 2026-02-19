"""
Test script to verify cost_price calculation with weighted average
"""

def test_weighted_average():
    """Test weighted average cost calculation"""
    
    print("=" * 60)
    print("Testing Weighted Average Cost Price Calculation")
    print("=" * 60)
    print()
    
    # Test Case 1: New product (no existing stock)
    print("Test Case 1: New Product (No Existing Stock)")
    print("-" * 60)
    current_stock = 0
    current_cost = 0
    new_quantity = 100
    new_unit_price = 10.50
    
    if current_stock > 0:
        total_cost = (current_cost * current_stock) + (new_unit_price * new_quantity)
        total_qty = current_stock + new_quantity
        new_cost_price = total_cost / total_qty
    else:
        new_cost_price = new_unit_price
    
    print(f"Current Stock: {current_stock} units")
    print(f"Current Cost Price: {current_cost:.2f}€")
    print(f"New Purchase: {new_quantity} units @ {new_unit_price:.2f}€")
    print(f"New Cost Price: {new_cost_price:.2f}€")
    print(f"Total Stock: {current_stock + new_quantity} units")
    print(f"Total Inventory Value: {(current_stock + new_quantity) * new_cost_price:.2f}€")
    print()
    
    # Test Case 2: Existing stock with different price
    print("Test Case 2: Existing Stock + New Purchase")
    print("-" * 60)
    current_stock = 100
    current_cost = 10.50
    new_quantity = 50
    new_unit_price = 12.00
    
    total_cost = (current_cost * current_stock) + (new_unit_price * new_quantity)
    total_qty = current_stock + new_quantity
    new_cost_price = total_cost / total_qty
    
    print(f"Current Stock: {current_stock} units @ {current_cost:.2f}€")
    print(f"Current Inventory Value: {current_stock * current_cost:.2f}€")
    print(f"New Purchase: {new_quantity} units @ {new_unit_price:.2f}€")
    print(f"Purchase Value: {new_quantity * new_unit_price:.2f}€")
    print(f"New Cost Price (Weighted Avg): {new_cost_price:.2f}€")
    print(f"Total Stock: {total_qty} units")
    print(f"Total Inventory Value: {total_qty * new_cost_price:.2f}€")
    print()
    
    # Test Case 3: With discount
    print("Test Case 3: Purchase with Discount")
    print("-" * 60)
    current_stock = 150
    current_cost = 11.00
    new_quantity = 75
    unit_price = 15.00
    discount_percent = 10.0
    
    # Calculate unit cost after discount
    item_subtotal = new_quantity * unit_price
    item_discount = item_subtotal * (discount_percent / 100)
    unit_cost = (item_subtotal - item_discount) / new_quantity
    
    total_cost = (current_cost * current_stock) + (unit_cost * new_quantity)
    total_qty = current_stock + new_quantity
    new_cost_price = total_cost / total_qty
    
    print(f"Current Stock: {current_stock} units @ {current_cost:.2f}€")
    print(f"Current Inventory Value: {current_stock * current_cost:.2f}€")
    print(f"New Purchase: {new_quantity} units @ {unit_price:.2f}€")
    print(f"Discount: {discount_percent}%")
    print(f"Unit Cost After Discount: {unit_cost:.2f}€")
    print(f"Purchase Value: {new_quantity * unit_cost:.2f}€")
    print(f"New Cost Price (Weighted Avg): {new_cost_price:.2f}€")
    print(f"Total Stock: {total_qty} units")
    print(f"Total Inventory Value: {total_qty * new_cost_price:.2f}€")
    print()
    
    # Test Case 4: Your actual case
    print("Test Case 4: Your Actual Purchase")
    print("-" * 60)
    purchase_total_with_tax = 34937.78
    inventory_value = 34920.07
    difference = purchase_total_with_tax - inventory_value
    
    # Assuming 18% tax
    purchase_without_tax = purchase_total_with_tax / 1.18
    tax_amount = purchase_total_with_tax - purchase_without_tax
    
    print(f"Purchase Total (with tax): {purchase_total_with_tax:.2f}€")
    print(f"Tax (18%): {tax_amount:.2f}€")
    print(f"Purchase Total (without tax): {purchase_without_tax:.2f}€")
    print(f"Current Inventory Value: {inventory_value:.2f}€")
    print(f"Difference: {difference:.2f}€ ({(difference/purchase_total_with_tax)*100:.4f}%)")
    print()
    print("Note: After the fix, inventory value should match purchase value (without tax)")
    print(f"Expected Inventory Value: {purchase_without_tax:.2f}€")
    print()
    
    print("=" * 60)
    print("Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_weighted_average()

