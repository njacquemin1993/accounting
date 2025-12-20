"""
Translation strings for the accounting application.
"""

TRANSLATIONS = {
    "en": {
        # App title and main navigation
        "app_title": "Simple Accounting System",
        "tab_chart_of_accounts": "📊 Chart of Accounts",
        "tab_journal_entries": "📝 Journal Entries",
        "tab_account_balances": "⚖️ Account Balances",
        "tab_result_sheet": "📈 Result Sheet",
        "tab_balance_sheet": "📋 Balance Sheet",
        "language_selector": "Language",
        
        # Chart of Accounts tab
        "chart_of_accounts": "Chart of Accounts",
        "no_accounts_found": "No accounts found. Add your first account below.",
        "add_new_account": "Add New Account",
        "account_code": "Account Code",
        "account_name": "Account Name",
        "category": "Category",
        "add_account": "Add Account",
        "account_code_help": "e.g., 1000, 2000, etc.",
        "account_name_help": "e.g., Cash, Accounts Payable",
        "account_exists": "An account with this code already exists.",
        "account_added": "Account added successfully!",
        "fill_all_fields": "Please fill in all fields.",
        
        # Categories
        "active": "Active",
        "passive": "Passive",
        "expenses": "Expenses",
        "products": "Products",
        
        # Journal Entries tab
        "journal_entries": "Journal Entries",
        "recent_journal_entries": "Recent Journal Entries",
        "add_new_journal_entry": "Add New Journal Entry",
        "date": "Date",
        "description": "Description",
        "debit_account": "Debit Account",
        "credit_account": "Credit Account",
        "amount": "Amount",
        "counterparty": "Counterparty",
        "add_entry": "Add Entry",
        "need_two_accounts": "You need at least 2 active accounts to create journal entries.",
        "amount_help": "Enter amount in CHF",
        "journal_entry_added": "Journal entry added successfully!",
        "invalid_entry": "Invalid journal entry. Please check your inputs.",
        
        # Account Balances tab
        "account_balances": "Account Balances",
        "filter_by_category": "Filter by Category",
        "all": "All",
        "account_details": "Account Details",
        "select_account": "Select an account to view details",
        "account_balance": "Account Balance",
        "entries_for": "Entries for",
        "no_entries_found": "No entries found for this account.",
        "no_balances_display": "No account balances to display. Add some journal entries first.",
        
        # Result Sheet tab
        "result_sheet": "Result Sheet (Income Statement)",
        "products_title": "Products",
        "expenses_title": "Expenses",
        "total_products": "TOTAL PRODUCTS",
        "total_expenses": "TOTAL EXPENSES",
        "net_income": "NET INCOME",
        "net_loss": "NET LOSS",
        "account_column": "Account",
        "amount_column": "Amount",
        
        # Balance Sheet tab
        "balance_sheet": "Balance Sheet",
        "active_title": "Active",
        "passive_title": "Passive",
        "total_active": "TOTAL ACTIVE",
        "total_passive": "TOTAL PASSIVE",
        "retained_earnings": "Retained Earnings",
        
        # Common
        "id": "ID",
        "code": "Code",
        "name": "Name",
        "balance": "Balance",
        "balance_sheet_balanced": "Balance Sheet is balanced!",
        "balance_sheet_not_balanced": "Balance Sheet is not balanced. Difference:",
        "net_income_included": "Current period net income of",
        "net_loss_included": "Current period net loss of",
        "has_been_included_passive": "has been included in passive.",
        "profit_margin": "Profit Margin",
        "no_products_display": "No products to display",
        "no_expenses_display": "No expenses to display",
        "no_active_accounts_display": "No active accounts to display",
        "no_passive_accounts_display": "No passive accounts to display",
        
        # Chart of Accounts - Account deactivation
        "deactivate_account": "Deactivate Account",
        "select_account_deactivate": "Select Account to Deactivate",
        "account_deactivated": "Account deactivated!",
        
        # Balance Sheet - Status messages
        "balance_sheet_balanced_checkmark": "✅ Balance Sheet is balanced!",
        "balance_sheet_not_balanced_x": "❌ Balance Sheet is not balanced. Difference:",
        "net_income_info": "💰 Current period net income of",
        "net_loss_warning": "⚠️ Current period net loss of",
        "has_been_included_in_passive": "has been included in passive.",
    },
    
    "fr": {
        # App title and main navigation
        "app_title": "Système Comptable Simple",
        "tab_chart_of_accounts": "📊 Plan Comptable",
        "tab_journal_entries": "📝 Écritures",
        "tab_account_balances": "⚖️ Soldes des Comptes",
        "tab_result_sheet": "📈 Compte de Résultat",
        "tab_balance_sheet": "📋 Bilan",
        "language_selector": "Langue",
        
        # Chart of Accounts tab
        "chart_of_accounts": "Plan Comptable",
        "no_accounts_found": "Aucun compte trouvé. Ajoutez votre premier compte ci-dessous.",
        "add_new_account": "Ajouter un Nouveau Compte",
        "account_code": "Code du Compte",
        "account_name": "Nom du Compte",
        "category": "Catégorie",
        "add_account": "Ajouter le Compte",
        "account_code_help": "ex: 1000, 2000, etc.",
        "account_name_help": "ex: Caisse, Fournisseurs",
        "account_exists": "Un compte avec ce code existe déjà.",
        "account_added": "Compte ajouté avec succès !",
        "fill_all_fields": "Veuillez remplir tous les champs.",
        
        # Categories
        "active": "Actif",
        "passive": "Passif",
        "expenses": "Charges",
        "products": "Produits",
        
        # Journal Entries tab
        "journal_entries": "Écritures Comptables",
        "recent_journal_entries": "Écritures Récentes",
        "add_new_journal_entry": "Ajouter une Nouvelle Écriture",
        "date": "Date",
        "description": "Description",
        "debit_account": "Compte Débiteur",
        "credit_account": "Compte Créditeur",
        "amount": "Montant",
        "counterparty": "Contrepartie",
        "add_entry": "Ajouter l'Écriture",
        "need_two_accounts": "Vous avez besoin d'au moins 2 comptes actifs pour créer des écritures.",
        "amount_help": "Entrez le montant en CHF",
        "journal_entry_added": "Écriture ajoutée avec succès !",
        "invalid_entry": "Écriture invalide. Veuillez vérifier vos saisies.",
        
        # Account Balances tab
        "account_balances": "Soldes des Comptes",
        "filter_by_category": "Filtrer par Catégorie",
        "all": "Tous",
        "account_details": "Détails du Compte",
        "select_account": "Sélectionnez un compte pour voir les détails",
        "account_balance": "Solde du Compte",
        "entries_for": "Écritures pour",
        "no_entries_found": "Aucune écriture trouvée pour ce compte.",
        "no_balances_display": "Aucun solde de compte à afficher. Ajoutez d'abord des écritures.",
        
        # Result Sheet tab
        "result_sheet": "Compte de Résultat",
        "products_title": "Produits",
        "expenses_title": "Charges",
        "total_products": "TOTAL PRODUITS",
        "total_expenses": "TOTAL CHARGES",
        "net_income": "BÉNÉFICE NET",
        "net_loss": "PERTE NETTE",
        "account_column": "Compte",
        "amount_column": "Montant",
        
        # Balance Sheet tab
        "balance_sheet": "Bilan",
        "active_title": "Actif",
        "passive_title": "Passif",
        "total_active": "TOTAL ACTIF",
        "total_passive": "TOTAL PASSIF",
        "retained_earnings": "Bénéfices Reportés",
        
        # Common
        "id": "ID",
        "code": "Code",
        "name": "Nom",
        "balance": "Solde",
        "balance_sheet_balanced": "Bilan équilibré !",
        "balance_sheet_not_balanced": "Bilan non équilibré. Différence :",
        "net_income_included": "Bénéfice net de la période de",
        "net_loss_included": "Perte nette de la période de",
        "has_been_included_passive": "a été inclus dans le passif.",
        "profit_margin": "Marge Bénéficiaire",
        "no_products_display": "Aucun produit à afficher",
        "no_expenses_display": "Aucune charge à afficher",
        "no_active_accounts_display": "Aucun compte actif à afficher",
        "no_passive_accounts_display": "Aucun compte passif à afficher",
        
        # Chart of Accounts - Account deactivation
        "deactivate_account": "Désactiver le Compte",
        "select_account_deactivate": "Sélectionnez le Compte à Désactiver",
        "account_deactivated": "Compte désactivé !",
        
        # Balance Sheet - Status messages
        "balance_sheet_balanced_checkmark": "✅ Bilan équilibré !",
        "balance_sheet_not_balanced_x": "❌ Bilan non équilibré. Différence :",
        "net_income_info": "💰 Bénéfice net de la période de",
        "net_loss_warning": "⚠️ Perte nette de la période de",
        "has_been_included_in_passive": "a été inclus dans le passif.",
    },
    
    "de": {
        # App title and main navigation
        "app_title": "Einfaches Buchhaltungssystem",
        "tab_chart_of_accounts": "📊 Kontenplan",
        "tab_journal_entries": "📝 Journalbuchungen",
        "tab_account_balances": "⚖️ Kontosalden",
        "tab_result_sheet": "📈 Erfolgsrechnung",
        "tab_balance_sheet": "📋 Bilanz",
        "language_selector": "Sprache",
        
        # Chart of Accounts tab
        "chart_of_accounts": "Kontenplan",
        "no_accounts_found": "Keine Konten gefunden. Fügen Sie Ihr erstes Konto unten hinzu.",
        "add_new_account": "Neues Konto Hinzufügen",
        "account_code": "Kontonummer",
        "account_name": "Kontoname",
        "category": "Kategorie",
        "add_account": "Konto Hinzufügen",
        "account_code_help": "z.B. 1000, 2000, etc.",
        "account_name_help": "z.B. Kasse, Kreditoren",
        "account_exists": "Ein Konto mit dieser Nummer existiert bereits.",
        "account_added": "Konto erfolgreich hinzugefügt!",
        "fill_all_fields": "Bitte füllen Sie alle Felder aus.",
        
        # Categories
        "active": "Aktiven",
        "passive": "Passiven",
        "expenses": "Aufwand",
        "products": "Ertrag",
        
        # Journal Entries tab
        "journal_entries": "Journalbuchungen",
        "recent_journal_entries": "Aktuelle Journalbuchungen",
        "add_new_journal_entry": "Neue Journalbuchung Hinzufügen",
        "date": "Datum",
        "description": "Beschreibung",
        "debit_account": "Sollkonto",
        "credit_account": "Habenkonto",
        "amount": "Betrag",
        "counterparty": "Gegenkonto",
        "add_entry": "Buchung Hinzufügen",
        "need_two_accounts": "Sie benötigen mindestens 2 aktive Konten für Buchungen.",
        "amount_help": "Betrag in CHF eingeben",
        "journal_entry_added": "Journalbuchung erfolgreich hinzugefügt!",
        "invalid_entry": "Ungültige Buchung. Bitte überprüfen Sie Ihre Eingaben.",
        
        # Account Balances tab
        "account_balances": "Kontosalden",
        "filter_by_category": "Nach Kategorie Filtern",
        "all": "Alle",
        "account_details": "Kontodetails",
        "select_account": "Wählen Sie ein Konto für Details",
        "account_balance": "Kontosaldo",
        "entries_for": "Buchungen für",
        "no_entries_found": "Keine Buchungen für dieses Konto gefunden.",
        "no_balances_display": "Keine Kontosalden zum Anzeigen. Fügen Sie zuerst Buchungen hinzu.",
        
        # Result Sheet tab
        "result_sheet": "Erfolgsrechnung",
        "products_title": "Ertrag",
        "expenses_title": "Aufwand",
        "total_products": "TOTAL ERTRAG",
        "total_expenses": "TOTAL AUFWAND",
        "net_income": "NETTOGEWINN",
        "net_loss": "NETTOVERLUST",
        "account_column": "Konto",
        "amount_column": "Betrag",
        
        # Balance Sheet tab
        "balance_sheet": "Bilanz",
        "active_title": "Aktiven",
        "passive_title": "Passiven",
        "total_active": "TOTAL AKTIVEN",
        "total_passive": "TOTAL PASSIVEN",
        "retained_earnings": "Gewinnvortrag",
        
        # Common
        "id": "ID",
        "code": "Code",
        "name": "Name",
        "balance": "Saldo",
        "balance_sheet_balanced": "Bilanz ist ausgeglichen!",
        "balance_sheet_not_balanced": "Bilanz ist nicht ausgeglichen. Differenz:",
        "net_income_included": "Nettogewinn der Periode von",
        "net_loss_included": "Nettoverlust der Periode von",
        "has_been_included_passive": "wurde in den Passiven einbezogen.",
        "profit_margin": "Gewinnmarge",
        "no_products_display": "Keine Erträge anzuzeigen",
        "no_expenses_display": "Keine Aufwände anzuzeigen",
        "no_active_accounts_display": "Keine Aktiven anzuzeigen",
        "no_passive_accounts_display": "Keine Passiven anzuzeigen",
        
        # Chart of Accounts - Account deactivation
        "deactivate_account": "Konto Deaktivieren",
        "select_account_deactivate": "Konto zum Deaktivieren Auswählen",
        "account_deactivated": "Konto deaktiviert!",
        
        # Balance Sheet - Status messages
        "balance_sheet_balanced_checkmark": "✅ Bilanz ist ausgeglichen!",
        "balance_sheet_not_balanced_x": "❌ Bilanz ist nicht ausgeglichen. Differenz:",
        "net_income_info": "💰 Nettogewinn der Periode von",
        "net_loss_warning": "⚠️ Nettoverlust der Periode von",
        "has_been_included_in_passive": "wurde in den Passiven einbezogen.",
    }
}

def get_translation(key: str, language: str = "en") -> str:
    """Get translation for a given key and language."""
    return TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(key, key)

def get_available_languages() -> dict:
    """Get available languages with their display names."""
    return {
        "en": "English",
        "fr": "Français", 
        "de": "Deutsch"
    }
