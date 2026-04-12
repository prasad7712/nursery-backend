"""Admin service for shared business logic"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models.admin import AdminLog
from src.models.user import User
from src.models.admin import ProductInventory
from src.models.admin import InventoryLog


class AdminService:
    """Service handling admin operations"""
    
    async def log_admin_action(
        self,
        session: AsyncSession,
        admin_id: str,
        action_type: str,
        entity_type: str,
        entity_id: str,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log an admin action"""
        try:
            log_entry = AdminLog(
                admin_id=admin_id,
                action_type=action_type,
                entity_type=entity_type,
                entity_id=entity_id,
                old_values=json.dumps(old_values) if old_values else None,
                new_values=json.dumps(new_values) if new_values else None,
                reason=reason,
                ip_address=ip_address,
                user_agent=user_agent
            )
            session.add(log_entry)
            await session.flush()
            
            return {
                'id': log_entry.id,
                'admin_id': log_entry.admin_id,
                'action_type': log_entry.action_type,
                'entity_type': log_entry.entity_type,
                'entity_id': log_entry.entity_id,
                'old_values': old_values,
                'new_values': new_values,
                'reason': reason,
                'created_at': log_entry.created_at.isoformat()
            }
        except Exception as e:
            raise Exception(f"Error logging admin action: {str(e)}")
    
    async def get_admin_logs(
        self,
        session: AsyncSession,
        admin_id: Optional[str] = None,
        action_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get paginated admin logs"""
        try:
            # Build query
            query = select(AdminLog)
            
            if admin_id:
                query = query.where(AdminLog.admin_id == admin_id)
            if action_type:
                query = query.where(AdminLog.action_type == action_type)
            if entity_type:
                query = query.where(AdminLog.entity_type == entity_type)
            
            # Count total
            count_query = select(func.count(AdminLog.id))
            if admin_id:
                count_query = count_query.where(AdminLog.admin_id == admin_id)
            if action_type:
                count_query = count_query.where(AdminLog.action_type == action_type)
            if entity_type:
                count_query = count_query.where(AdminLog.entity_type == entity_type)
            
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # Get paginated results (ordered by created_at descending)
            query = query.order_by(AdminLog.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(query)
            logs = result.scalars().all()
            
            logs_list = [
                {
                    'id': log.id,
                    'admin_id': log.admin_id,
                    'action_type': log.action_type,
                    'entity_type': log.entity_type,
                    'entity_id': log.entity_id,
                    'old_values': json.loads(log.old_values) if log.old_values else None,
                    'new_values': json.loads(log.new_values) if log.new_values else None,
                    'reason': log.reason,
                    'created_at': log.created_at.isoformat()
                }
                for log in logs
            ]
            
            return {
                'logs': logs_list,
                'total': total,
                'page': page,
                'per_page': per_page
            }
        except Exception as e:
            raise Exception(f"Error fetching admin logs: {str(e)}")
    
    async def change_user_role(
        self,
        session: AsyncSession,
        admin_id: str,
        user_id: str,
        new_role: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Change user role (admin only)"""
        try:
            # Get old user data
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError("User not found")
            
            old_role = user.role
            
            # Update user role
            user.role = new_role
            session.add(user)
            await session.flush()
            
            # Log the action
            await self.log_admin_action(
                session=session,
                admin_id=admin_id,
                action_type='ROLE_CHANGE',
                entity_type='User',
                entity_id=user_id,
                old_values={'role': old_role},
                new_values={'role': new_role},
                reason=reason
            )
            
            await session.commit()
            
            return {
                'success': True,
                'user_id': user_id,
                'old_role': old_role,
                'new_role': new_role
            }
        except Exception as e:
            raise Exception(f"Error changing user role: {str(e)}")
    
    async def deactivate_user(
        self,
        session: AsyncSession,
        admin_id: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deactivate a user"""
        try:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError("User not found")
            
            user.is_active = False
            session.add(user)
            await session.flush()
            
            await self.log_admin_action(
                session=session,
                admin_id=admin_id,
                action_type='DEACTIVATE',
                entity_type='User',
                entity_id=user_id,
                old_values={'is_active': True},
                new_values={'is_active': False},
                reason=reason
            )
            
            await session.commit()
            
            return {'success': True, 'user_id': user_id, 'is_active': False}
        except Exception as e:
            await session.rollback()
            raise Exception(f"Error deactivating user: {str(e)}")
    
    async def activate_user(
        self,
        session: AsyncSession,
        admin_id: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Activate a user"""
        try:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError("User not found")
            
            user.is_active = True
            session.add(user)
            await session.flush()
            
            await self.log_admin_action(
                session=session,
                admin_id=admin_id,
                action_type='ACTIVATE',
                entity_type='User',
                entity_id=user_id,
                old_values={'is_active': False},
                new_values={'is_active': True},
                reason=reason
            )
            
            await session.commit()
            
            return {'success': True, 'user_id': user_id, 'is_active': True}
        except Exception as e:
            await session.rollback()
            await self.log_admin_action(
                admin_id=admin_id,
                action_type='ACTIVATE',
                entity_type='User',
                entity_id=user_id,
                old_values={'is_active': False},
                new_values={'is_active': True},
                reason=reason
            )
            
            return {'success': True, 'user_id': user_id, 'is_active': True}
        except Exception as e:
            raise Exception(f"Error activating user: {str(e)}")
    
    async def adjust_inventory(
        self,
        session: AsyncSession,
        admin_id: str,
        inventory_id: str,
        change_type: str,
        quantity: int,
        reason: str,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """Adjust product inventory"""
        try:
            result = await session.execute(
                select(ProductInventory).where(ProductInventory.id == inventory_id)
            )
            inventory = result.scalar_one_or_none()
            
            if not inventory:
                raise ValueError("Inventory not found")
            
            old_quantity = inventory.quantity
            
            # Adjust quantity
            if change_type == "ADD":
                inventory.quantity += quantity
            elif change_type == "REMOVE":
                if inventory.quantity < quantity:
                    raise ValueError("Insufficient inventory to remove")
                inventory.quantity -= quantity
            else:
                raise ValueError("Invalid change_type. Must be 'ADD' or 'REMOVE'")
            
            session.add(inventory)
            await session.flush()
            
            # Log inventory adjustment
            inv_log = InventoryLog(
                inventory_id=inventory_id,
                change_type=change_type,
                quantity_change=quantity,
                old_quantity=old_quantity,
                new_quantity=inventory.quantity,
                reason=reason,
                note=note,
                admin_id=admin_id
            )
            session.add(inv_log)
            
            # Log admin action
            await self.log_admin_action(
                session=session,
                admin_id=admin_id,
                action_type='INVENTORY_ADJUST',
                entity_type='ProductInventory',
                entity_id=inventory_id,
                old_values={'quantity': old_quantity},
                new_values={'quantity': inventory.quantity},
                reason=reason
            )
            
            await session.commit()
            
            return {
                'success': True,
                'inventory_id': inventory_id,
                'old_quantity': old_quantity,
                'new_quantity': inventory.quantity,
                'change_type': change_type,
                'quantity_change': quantity
            }
        except Exception as e:
            await session.rollback()
            raise Exception(f"Error adjusting inventory: {str(e)}")
    
    async def get_low_stock_products(
        self,
        session: AsyncSession,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get products with low stock levels"""
        try:
            from sqlalchemy.orm import selectinload
            
            # Query for low stock items
            stmt = select(ProductInventory).where(
                ProductInventory.stock_level <= ProductInventory.low_stock_threshold
            ).options(selectinload(ProductInventory.product))
            
            # Count total
            count_stmt = select(func.count()).select_from(ProductInventory).where(
                ProductInventory.stock_level <= ProductInventory.low_stock_threshold
            )
            total_result = await session.execute(count_stmt)
            total = total_result.scalar() or 0
            
            # Get paginated results
            stmt = stmt.offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(stmt)
            inventories = result.scalars().all()
            
            return {
                'inventories': inventories,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        except Exception as e:
            raise Exception(f"Error fetching low stock products: {str(e)}")


# Singleton instance
admin_service = AdminService()
