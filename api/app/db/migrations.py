"""
Database migrations for schema updates
"""

import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def run_migrations(db: AsyncSession) -> None:
    """Run database migrations for schema updates."""

    migrations = [
        # Migration 1: Add SLURM cluster fields to orders table (v2.0.0)
        {
            "name": "add_slurm_fields_to_orders",
            "sql_statements": [
                "ALTER TABLE orders ADD COLUMN IF NOT EXISTS cluster_name VARCHAR(255)",
                "ALTER TABLE orders ADD COLUMN IF NOT EXISTS slurm_job_id VARCHAR(255)",
                "CREATE INDEX IF NOT EXISTS idx_orders_cluster_name ON orders(cluster_name)",
                "CREATE INDEX IF NOT EXISTS idx_orders_slurm_job_id ON orders(slurm_job_id)"
            ],
            "description": "Add SLURM cluster fields to orders table"
        }
    ]

    for migration in migrations:
        try:
            logger.info(f"Running migration: {migration['name']} - {migration['description']}")

            # Execute the migration SQL statements
            sql_statements = migration.get("sql_statements", [migration.get("sql", "")])

            for sql in sql_statements:
                if sql.strip():  # Skip empty statements
                    await db.execute(text(sql))

            await db.commit()

            logger.info(f"Migration completed: {migration['name']}")

        except Exception as e:
            logger.warning(f"Migration failed: {migration['name']} - {str(e)}")
            # Continue with other migrations even if one fails
            await db.rollback()
