# 🔧 SQLAlchemy Quick Reference Guide

## Common Query Patterns

### 1. Select Single Record

```python
from sqlalchemy import select
from src.models.user import User

# Get by ID
stmt = select(User).where(User.id == user_id)
result = await session.execute(stmt)
user = result.scalar_one_or_none()  # Returns None if not found

# Get by email
stmt = select(User).where(User.email == email)
result = await session.execute(stmt)
user = result.scalar_one()  # Raises error if not found
```

### 2. Select Multiple Records

```python
# Get all users
stmt = select(User)
result = await session.execute(stmt)
users = result.scalars().all()

# Get with filter
stmt = select(User).where(User.is_active == True)
result = await session.execute(stmt)
active_users = result.scalars().all()

# Get with multiple conditions
from sqlalchemy import and_, or_

stmt = select(User).where(
    and_(
        User.is_active == True,
        User.role == UserRoleEnum.CUSTOMER
    )
)
result = await session.execute(stmt)
customers = result.scalars().all()
```

### 3. Pagination

```python
from sqlalchemy import select, func

# Count total
count_stmt = select(func.count()).select_from(User)
total = await session.scalar(count_stmt)

# Get page
page = 1
per_page = 10
offset = (page - 1) * per_page

stmt = select(User).offset(offset).limit(per_page)
result = await session.execute(stmt)
users = result.scalars().all()
```

### 4. Relationships (Eager Loading)

```python
from sqlalchemy.orm import selectinload, joinedload

# Load with relationships
stmt = select(Order).options(
    selectinload(Order.items),
    selectinload(Order.user)
).where(Order.id == order_id)

result = await session.execute(stmt)
order = result.scalar_one_or_none()

# Access relationships
if order:
    print(order.user.email)
    for item in order.items:
        print(item.product.name)
```

### 5. Insert Record

```python
from src.models.user import User
import uuid

# Create new user
new_user = User(
    id=str(uuid.uuid4()),
    email="user@example.com",
    password_hash="hashed_password",
    first_name="John",
    last_name="Doe",
    role=UserRoleEnum.CUSTOMER,
    is_active=True
)

session.add(new_user)
await session.commit()
await session.refresh(new_user)  # Get updated data from DB
```

### 6. Update Record

```python
# Method 1: Update object
stmt = select(User).where(User.id == user_id)
result = await session.execute(stmt)
user = result.scalar_one()

user.first_name = "Updated Name"
user.is_active = False

await session.commit()
await session.refresh(user)

# Method 2: Direct update
from sqlalchemy import update

stmt = update(User).where(User.id == user_id).values(
    first_name="Updated Name",
    is_active=False
)
await session.execute(stmt)
await session.commit()
```

### 7. Delete Record

```python
# Method 1: Delete object
stmt = select(User).where(User.id == user_id)
result = await session.execute(stmt)
user = result.scalar_one()

await session.delete(user)
await session.commit()

# Method 2: Direct delete
from sqlalchemy import delete

stmt = delete(User).where(User.id == user_id)
await session.execute(stmt)
await session.commit()
```

### 8. Search with LIKE

```python
# Case-insensitive search
search_term = "john"
stmt = select(User).where(
    or_(
        User.first_name.ilike(f"%{search_term}%"),
        User.last_name.ilike(f"%{search_term}%"),
        User.email.ilike(f"%{search_term}%")
    )
)
result = await session.execute(stmt)
users = result.scalars().all()
```

### 9. Ordering

```python
# Order by single column
stmt = select(Product).order_by(Product.created_at.desc())

# Order by multiple columns
stmt = select(Product).order_by(
    Product.category_id.asc(),
    Product.price.desc()
)

result = await session.execute(stmt)
products = result.scalars().all()
```

### 10. Aggregations

```python
from sqlalchemy import func

# Count
count_stmt = select(func.count()).select_from(User)
total_users = await session.scalar(count_stmt)

# Sum
sum_stmt = select(func.sum(Order.total_amount)).where(
    Order.status == OrderStatusEnum.DELIVERED
)
total_revenue = await session.scalar(sum_stmt)

# Average
avg_stmt = select(func.avg(Product.price))
avg_price = await session.scalar(avg_stmt)

# Group by
stmt = select(
    Product.category_id,
    func.count(Product.id).label('product_count')
).group_by(Product.category_id)

result = await session.execute(stmt)
category_counts = result.all()
```

### 11. Joins

```python
# Inner join
stmt = select(Order, User).join(User, Order.user_id == User.id)
result = await session.execute(stmt)
orders_with_users = result.all()

# Left outer join
stmt = select(Product).outerjoin(
    ProductInventory,
    Product.id == ProductInventory.product_id
)
result = await session.execute(stmt)
products = result.scalars().all()
```

### 12. Transactions

```python
# Manual transaction control
try:
    # Create order
    order = Order(...)
    session.add(order)
    
    # Create order items
    for item_data in items:
        order_item = OrderItem(...)
        session.add(order_item)
    
    # Update inventory
    inventory.stock_level -= quantity
    
    # Commit all changes
    await session.commit()
    
except Exception as e:
    # Rollback on error
    await session.rollback()
    raise
```

### 13. Exists Check

```python
from sqlalchemy import exists

# Check if email exists
stmt = select(exists().where(User.email == email))
email_exists = await session.scalar(stmt)

if email_exists:
    raise ValueError("Email already registered")
```

### 14. Subqueries

```python
# Get users with orders
from sqlalchemy import exists

stmt = select(User).where(
    exists().where(Order.user_id == User.id)
)
result = await session.execute(stmt)
users_with_orders = result.scalars().all()
```

### 15. Raw SQL (when needed)

```python
from sqlalchemy import text

# Execute raw SQL
stmt = text("SELECT * FROM users WHERE email = :email")
result = await session.execute(stmt, {"email": email})
user = result.first()
```

---

## Common Patterns in Your Project

### Get User Cart

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.cart import Cart

stmt = select(Cart).options(
    selectinload(Cart.items).selectinload(CartItem.product)
).where(Cart.user_id == user_id)

result = await session.execute(stmt)
cart = result.scalar_one_or_none()
```

### Create Order from Cart

```python
# Get cart with items
cart = await get_cart(session, user_id)

# Create order
order = Order(
    id=generate_id(),
    user_id=user_id,
    total_amount=calculate_total(cart.items),
    status=OrderStatusEnum.PENDING
)
session.add(order)

# Create order items
for cart_item in cart.items:
    order_item = OrderItem(
        id=generate_id(),
        order_id=order.id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        unit_price=cart_item.product.price,
        subtotal=cart_item.quantity * cart_item.product.price
    )
    session.add(order_item)

# Clear cart
for item in cart.items:
    await session.delete(item)

await session.commit()
```

### Admin Dashboard Stats

```python
from sqlalchemy import func, select
from src.models.user import User
from src.models.order import Order
from src.models.product import Product

# Total users
total_users = await session.scalar(
    select(func.count()).select_from(User)
)

# Total orders
total_orders = await session.scalar(
    select(func.count()).select_from(Order)
)

# Total revenue
total_revenue = await session.scalar(
    select(func.sum(Order.total_amount)).where(
        Order.status == OrderStatusEnum.DELIVERED
    )
)

# Active products
active_products = await session.scalar(
    select(func.count()).select_from(Product).where(
        Product.is_active == True
    )
)
```

---

## Error Handling

```python
from sqlalchemy.exc import IntegrityError, NoResultFound

try:
    # Database operation
    result = await session.execute(stmt)
    user = result.scalar_one()
    
except NoResultFound:
    raise HTTPException(status_code=404, detail="User not found")
    
except IntegrityError as e:
    await session.rollback()
    if "unique constraint" in str(e).lower():
        raise HTTPException(status_code=400, detail="Email already exists")
    raise HTTPException(status_code=400, detail="Database constraint violation")
    
except Exception as e:
    await session.rollback()
    raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
```

---

## Best Practices

1. **Always use `Depends(get_session)`** in controllers
2. **Use `selectinload` or `joinedload`** for relationships
3. **Use `scalar_one_or_none()`** when record might not exist
4. **Use `scalar_one()`** when record must exist
5. **Always handle exceptions** and rollback on errors
6. **Use indexes** on frequently queried columns
7. **Use `func.count()`** for counting instead of loading all records
8. **Use pagination** for large result sets
9. **Use transactions** for multi-step operations
10. **Refresh objects** after commit if you need updated data

---

## Performance Tips

1. **Eager load relationships** to avoid N+1 queries
2. **Use `select(func.count())`** instead of `len(results)`
3. **Add indexes** on foreign keys and frequently filtered columns
4. **Use connection pooling** (already configured)
5. **Limit result sets** with pagination
6. **Use `exists()`** instead of counting when checking existence
7. **Batch operations** when possible
8. **Use `bulk_insert_mappings`** for large inserts

---

## Debugging

```python
# Enable SQL logging
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Print all SQL queries
)

# Print query
print(str(stmt.compile(compile_kwargs={"literal_binds": True})))
```

---

This guide covers the most common patterns you'll use in your FastAPI application with SQLAlchemy!
