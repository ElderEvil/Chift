from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base, TimestampMixin


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    odoo_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    partner_id: Mapped[int] = mapped_column(Integer, nullable=False)  # Odoo partner ID
    partner_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    invoice_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    amount_total: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)  # draft, posted, cancel, etc.
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"Invoice(id={self.id}, odoo_id={self.odoo_id}, number={self.invoice_number!r}, amount={self.amount_total})"
