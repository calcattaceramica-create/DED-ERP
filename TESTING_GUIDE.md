# Testing Guide: Cost Price Update Fix

## Overview
This guide will help you test the automatic cost_price update feature using weighted average method.

---

## What Was Fixed?

### Problem:
- When adding purchase invoices, the `cost_price` in the Product table was not updated
- Inventory value was calculated as `stock_qty × product.cost_price`
- If `cost_price` was outdated, inventory value was incorrect

### Solution:
- Automatic `cost_price` update using **Weighted Average Method**
- Updates happen when confirming purchase invoices
- Formula: `new_cost = (old_cost × old_qty + new_cost × new_qty) / total_qty`

---

## Testing Steps

### Step 1: Check Current Product Cost Price

1. Go to: **Inventory → Products**
2. Select a product you want to test
3. Note down:
   - Current Stock Quantity
   - Current Cost Price
   - Current Inventory Value = Stock × Cost Price

**Example:**
```
Product: Ceramic Tile A
Current Stock: 100 units
Current Cost Price: 10.00€
Current Inventory Value: 1,000.00€
```

---

### Step 2: Create a New Purchase Invoice

1. Go to: **Purchases → Purchase Invoices → Add Invoice**
2. Fill in the details:
   - Supplier: Choose any supplier
   - Warehouse: Choose a warehouse
   - Invoice Date: Today's date
3. Add the product you noted in Step 1:
   - Product: Ceramic Tile A
   - Quantity: 50 units
   - Unit Price: 12.00€
   - Discount: 0% (or any discount you want)
   - Tax: 18% (or your default tax rate)
4. Click **Save**

**Expected Calculation:**
```
Item Subtotal: 50 × 12.00€ = 600.00€
Discount (0%): 0.00€
Taxable Amount: 600.00€
Tax (18%): 108.00€
Total: 708.00€
```

---

### Step 3: Confirm the Purchase Invoice

1. After saving, you'll see the invoice details
2. Click **Confirm Invoice**
3. The system will:
   - Add 50 units to stock
   - Update cost_price using weighted average
   - Create stock movement record

**Expected Cost Price Calculation:**
```
Old Stock: 100 units @ 10.00€ = 1,000.00€
New Purchase: 50 units @ 12.00€ = 600.00€
Total: 150 units
Weighted Average: (1,000 + 600) / 150 = 10.67€
```

---

### Step 4: Verify the Cost Price Update

1. Go to: **Inventory → Products**
2. Open the same product (Ceramic Tile A)
3. Check the **Cost Price** field
4. It should now show: **10.67€** (instead of 10.00€)

---

### Step 5: Verify Inventory Value

1. Go to: **Reports → Inventory Report**
2. Find your product in the list
3. Check:
   - Stock Quantity: Should be 150 units
   - Cost Price: Should be 10.67€
   - Inventory Value: Should be 1,600.00€ (150 × 10.67)

**Verification:**
```
Old Inventory Value: 1,000.00€
+ Purchase Value (without tax): 600.00€
= New Inventory Value: 1,600.00€ ✓
```

---

### Step 6: Test with Discount

1. Create another purchase invoice for the same product
2. This time add a discount:
   - Quantity: 30 units
   - Unit Price: 15.00€
   - Discount: 10%
   - Tax: 18%

**Expected Calculation:**
```
Item Subtotal: 30 × 15.00€ = 450.00€
Discount (10%): 45.00€
Unit Cost After Discount: (450 - 45) / 30 = 13.50€
Taxable Amount: 405.00€
Tax (18%): 72.90€
Total: 477.90€
```

3. Confirm the invoice

**Expected Cost Price Calculation:**
```
Old Stock: 150 units @ 10.67€ = 1,600.50€
New Purchase: 30 units @ 13.50€ = 405.00€
Total: 180 units
Weighted Average: (1,600.50 + 405) / 180 = 11.14€
```

4. Verify the cost price is now **11.14€**

---

## Test Case: Your Actual Scenario

Based on your numbers:
- Purchase Total (with tax): 34,937.78€
- Current Inventory Value: 34,920.07€
- Difference: 17.71€

**After the fix:**
1. The purchase value (without tax) should be: 34,937.78€ / 1.18 = 29,608.29€
2. The inventory value should match this amount (assuming no previous stock)
3. The difference should be eliminated

---

## Important Notes

### Tax Handling:
- ✅ `cost_price` is calculated **WITHOUT tax**
- ✅ Inventory value = `stock_qty × cost_price` (without tax)
- ✅ Purchase total in reports **includes tax**

### Weighted Average Formula:
```
new_cost_price = (old_cost × old_qty + new_cost × new_qty) / (old_qty + new_qty)
```

### When Cost Price Updates:
- ✅ When confirming a purchase invoice
- ❌ NOT when creating a draft invoice
- ❌ NOT when canceling an invoice (stock is removed but cost_price stays)

---

## Troubleshooting

### Issue: Cost price didn't update
**Check:**
- Did you **confirm** the invoice? (not just save)
- Is the product set to **track inventory**?
- Are there any errors in the console/logs?

### Issue: Inventory value still doesn't match
**Check:**
- Are you comparing with tax or without tax?
- Do you have sales that reduced the stock?
- Are there multiple warehouses with different stock levels?

---

## Success Criteria

✅ Cost price updates automatically when confirming purchase invoices  
✅ Weighted average is calculated correctly  
✅ Inventory value matches purchase value (without tax)  
✅ Multiple purchases update the cost price progressively  
✅ Discounts are properly accounted for in cost calculation  

---

**Happy Testing! 🚀**

