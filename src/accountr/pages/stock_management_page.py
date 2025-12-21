"""
Stock Management page for inventory tracking.
"""

import streamlit as st
import pandas as pd
from accountr.database import StockItem, StockJournalEntry
from accountr.translation_utils import t
from accountr.pages.base_page import BasePage
from accountr.database_switcher import get_current_db_manager


@st.dialog(t("add_new_item"))
def show_add_item_dialog():
    """Show add new item dialog."""
    with st.form("add_item_form"):
        name = st.text_input(t("item_name"), help=t("item_name_help"))
        description = st.text_area(t("item_description"), help=t("item_description_help"))
        unit = st.selectbox(
            t("unit_of_measure"),
            options=["pieces", "kg", "g", "liters", "ml", "meters", "cm", "m2", "m3"],
            help=t("unit_of_measure_help"),
        )
        initial_quantity = st.number_input(
            t("initial_quantity"),
            min_value=0.0,
            value=0.0,
            step=0.1,
            help=t("initial_quantity_help"),
        )

        submit_button = st.form_submit_button(t("add_item"))

        if submit_button:
            if name.strip():
                db_manager = get_current_db_manager()
                session = db_manager.get_session()

                try:
                    # Check if item already exists
                    existing_item = session.query(StockItem).filter(StockItem.name == name.strip()).first()

                    if existing_item:
                        st.error(t("item_already_exists"))
                    else:
                        # Create new item
                        new_item = StockItem(
                            name=name.strip(),
                            description=description.strip(),
                            unit=unit,
                            current_quantity=initial_quantity,
                        )
                        session.add(new_item)
                        session.flush()  # To get the ID

                        # Create initial stock journal entry if quantity > 0
                        if initial_quantity > 0:
                            stock_entry = StockJournalEntry(
                                item_id=new_item.id,
                                quantity_change=initial_quantity,
                                previous_quantity=0.0,
                                new_quantity=initial_quantity,
                                description=t("initial_stock_entry"),
                            )
                            session.add(stock_entry)

                        session.commit()
                        st.success(t("item_added_successfully"))
                        st.rerun()

                except Exception as e:
                    session.rollback()
                    st.error(f"{t('error_adding_item')}: {str(e)}")
                finally:
                    session.close()
            else:
                st.error(t("item_name_required"))


@st.dialog(t("adjust_quantity"))
def show_quantity_adjustment_dialog(item_id: int, current_quantity: float):
    """Show quantity adjustment dialog."""
    with st.form("adjust_quantity_form"):
        st.write(f"{t('current_quantity')}: {current_quantity}")

        adjustment_type = st.radio(
            t("adjustment_type"),
            options=["add", "remove", "set"],
            format_func=lambda x: t(f"adjustment_type_{x}"),
            horizontal=True,
        )

        if adjustment_type in ["add", "remove"]:
            quantity = st.number_input(t("quantity"), min_value=0.1, value=1.0, step=0.1)
        else:  # set
            quantity = st.number_input(t("new_quantity"), min_value=0.0, value=current_quantity, step=0.1)

        description = st.text_area(t("adjustment_description"), help=t("adjustment_description_help"))

        submit_button = st.form_submit_button(t("apply_adjustment"))

        if submit_button:
            if description.strip():
                db_manager = get_current_db_manager()
                session = db_manager.get_session()

                try:
                    item = session.query(StockItem).filter(StockItem.id == item_id).first()

                    if item:
                        previous_quantity = item.current_quantity

                        # Calculate new quantity based on adjustment type
                        if adjustment_type == "add":
                            new_quantity = previous_quantity + quantity
                            quantity_change = quantity
                        elif adjustment_type == "remove":
                            new_quantity = max(0, previous_quantity - quantity)
                            quantity_change = -(previous_quantity - new_quantity)
                        else:  # set
                            new_quantity = quantity
                            quantity_change = new_quantity - previous_quantity

                        # Update item quantity
                        item.current_quantity = new_quantity

                        # Create stock journal entry
                        stock_entry = StockJournalEntry(
                            item_id=item.id,
                            quantity_change=quantity_change,
                            previous_quantity=previous_quantity,
                            new_quantity=new_quantity,
                            description=description.strip(),
                        )
                        session.add(stock_entry)

                        session.commit()
                        st.success(t("quantity_adjusted_successfully"))
                        st.rerun()
                    else:
                        st.error(t("item_not_found"))

                except Exception as e:
                    session.rollback()
                    st.error(f"{t('error_adjusting_quantity')}: {str(e)}")
                finally:
                    session.close()
            else:
                st.error(t("description_required"))


@st.dialog(t("stock_journal"))
def show_stock_journal_dialog(item_id: int):
    """Show stock journal entries for an item."""
    db_manager = get_current_db_manager()
    session = db_manager.get_session()

    try:
        item = session.query(StockItem).filter(StockItem.id == item_id).first()
        if not item:
            st.error(t("item_not_found"))
            return

        st.subheader(f"{t('stock_journal_for')} {item.name}")

        # Get stock journal entries
        entries = (
            session.query(StockJournalEntry)
            .filter(StockJournalEntry.item_id == item_id)
            .order_by(StockJournalEntry.date.desc())
            .all()
        )

        if entries:
            # Create DataFrame for display
            data = []
            for entry in entries:
                data.append(
                    {
                        t("date"): entry.date.strftime("%Y-%m-%d %H:%M"),
                        t("description"): entry.description,
                        t("quantity_change"): f"{entry.quantity_change:+.2f}",
                        t("previous_quantity"): f"{entry.previous_quantity:.2f}",
                        t("new_quantity"): f"{entry.new_quantity:.2f}",
                    }
                )

            df = pd.DataFrame(data)
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.info(t("no_stock_entries"))

    except Exception as e:
        st.error(f"{t('error_loading_journal')}: {str(e)}")
    finally:
        session.close()


class StockManagementPage(BasePage):
    def __init__(self):
        super().__init__("stock_management", "📦")

    def run(self):
        self._header("stock_management")

        db_manager = get_current_db_manager()
        session = db_manager.get_session()

        try:
            # Get all stock items
            items = session.query(StockItem).filter(StockItem.is_active).order_by(StockItem.name).all()

            if items:
                st.subheader(t("inventory_list"))

                # Create columns for the table header
                col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 2])
                with col1:
                    st.write(f"**{t('item_name')}**")
                with col2:
                    st.write(f"**{t('current_quantity')}**")
                with col3:
                    st.write(f"**{t('unit')}**")
                with col4:
                    st.write(f"**{t('actions')}**")
                with col5:
                    st.write("")
                with col6:
                    st.write("")

                st.divider()

                # Display each item
                for item in items:
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 2])

                    with col1:
                        st.write(f"**{item.name}**")
                        if item.description:
                            st.caption(item.description)

                    with col2:
                        # Color code based on quantity
                        if item.current_quantity == 0:
                            st.error(f"{item.current_quantity:.2f}")
                        elif item.current_quantity < 10:  # Low stock warning
                            st.warning(f"{item.current_quantity:.2f}")
                        else:
                            st.success(f"{item.current_quantity:.2f}")

                    with col3:
                        st.write(item.unit)

                    with col4:
                        if st.button(t("adjust"), key=f"adjust_{item.id}"):
                            show_quantity_adjustment_dialog(item.id, item.current_quantity)

                    with col5:
                        if st.button(t("journal"), key=f"journal_{item.id}"):
                            show_stock_journal_dialog(item.id)

                    with col6:
                        # Delete button (optional)
                        if st.button("🗑️", key=f"delete_{item.id}", help=t("delete_item")):
                            # Soft delete
                            item.is_active = False
                            session.commit()
                            st.rerun()

                    st.divider()
            else:
                st.info(t("no_items_in_stock"))

            # Add new item button
            st.markdown("---")
            if st.button(t("add_new_item"), type="primary"):
                show_add_item_dialog()

        except Exception as e:
            st.error(f"{t('error_loading_inventory')}: {str(e)}")
        finally:
            session.close()

        self._footer()
