import datetime
import sqlite3


class CRMDatabase:

    def __init__(self, db_name="crm_app.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                company TEXT
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                note TEXT,
                date TEXT,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        """
        )
        self.conn.commit()

    def add_client(self, name, email, phone, company):
        self.cursor.execute(
            """
            INSERT INTO clients (name, email, phone, company) 
            VALUES (?, ?, ?, ?)
        """,
            (name, email, phone, company),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def search_clients(self, keyword):
        query = f"%{keyword}%"
        self.cursor.execute(
            """
            SELECT * FROM clients 
            WHERE name LIKE ? OR company LIKE ?
        """,
            (query, query),
        )
        return self.cursor.fetchall()

    def update_client(self, client_id, name, email, phone, company):
        self.cursor.execute(
            """
            UPDATE clients 
            SET name=?, email=?, phone=?, company=?
            WHERE id=?
        """,
            (name, email, phone, company, client_id),
        )
        self.conn.commit()

    def delete_client(self, client_id):
        self.cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
        self.cursor.execute(
            "DELETE FROM interactions WHERE client_id=?", (client_id,)
        )
        self.conn.commit()

    def add_interaction(self, client_id, note):
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cursor.execute(
            """
            INSERT INTO interactions (client_id, note, date) 
            VALUES (?, ?, ?)
        """,
            (client_id, note, date_str),
        )
        self.conn.commit()

    def get_client_interactions(self, client_id):
        self.cursor.execute(
            """
            SELECT date, note FROM interactions 
            WHERE client_id = ? ORDER BY date DESC
        """,
            (client_id,),
        )
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


class CRMApp:

    def __init__(self):
        self.db = CRMDatabase()

    def main_menu(self):
        while True:
            print("\n" + "=" * 30)
            print("        PYTHON CRM        ")
            print("=" * 30)
            print("1. Add Client")
            print("2. Search / View Clients")
            print("3. Update Client")
            print("4. Delete Client")
            print("5. Add Interaction Note")
            print("6. View Interaction History")
            print("7. Exit")
            choice = input("\nEnter your choice (1-7): ")

            if choice == "1":
                self.action_add_client()
            elif choice == "2":
                self.action_search_clients()
            elif choice == "3":
                self.action_update_client()
            elif choice == "4":
                self.action_delete_client()
            elif choice == "5":
                self.action_add_interaction()
            elif choice == "6":
                self.action_view_interactions()
            elif choice == "7":
                self.db.close()
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def action_add_client(self):
        print("\n--- Add New Client ---")
        name = input("Name: ")
        email = input("Email: ")
        phone = input("Phone: ")
        company = input("Company: ")
        client_id = self.db.add_client(name, email, phone, company)
        print(f"Client {name} added successfully with ID {client_id}.")

    def action_search_clients(self):
        keyword = input("\nEnter name or company to search: ")
        results = self.db.search_clients(keyword)
        if not results:
            print("No clients found.")
        else:
            print("\n--- Search Results ---")
            for r in results:
                print(
                    f"ID: {r[0]} | Name: {r[1]} | Email: {r[2]} | Phone: {r[3]} | Company: {r[4]}"
                )
        return results

    def action_update_client(self):
        self.action_search_clients()
        client_id = input("\nEnter the ID of the client to update: ")
        print("\nEnter new details (press enter to skip updating a field):")

        # Basic prompt to edit/keep fields
        r = self.db.cursor.execute(
            "SELECT * FROM clients WHERE id=?", (client_id,)
        ).fetchone()
        if not r:
            print("Client ID not found.")
            return

        name = input(f"Name [{r[1]}]: ") or r[1]
        email = input(f"Email [{r[2]}]: ") or r[2]
        phone = input(f"Phone [{r[3]}]: ") or r[3]
        company = input(f"Company [{r[4]}]: ") or r[4]

        self.db.update_client(client_id, name, email, phone, company)
        print("Client information updated!")

    def action_delete_client(self):
        self.action_search_clients()
        client_id = input("\nEnter the ID of the client to delete: ")
        confirm = input(
            f"Are you sure you want to delete ID {client_id}? (y/n): "
        )
        if confirm.lower() == "y":
            self.db.delete_client(client_id)
            print("Client and all their interactions deleted.")

    def action_add_interaction(self):
        self.action_search_clients()
        client_id = input("\nEnter the ID of the client to add a note to: ")
        note = input("Enter interaction note (e.g., called about renewal): ")
        self.db.add_interaction(client_id, note)
        print("Interaction note saved!")

    def action_view_interactions(self):
        self.action_search_clients()
        client_id = input(
            "\nEnter the ID of the client to view interaction history: "
        )
        interactions = self.db.get_client_interactions(client_id)
        if not interactions:
            print("No interactions found for this client.")
        else:
            print(f"\n--- Interactions for Client ID {client_id} ---")
            for date, note in interactions:
                print(f"[{date}] - {note}")


if __name__ == "__main__":
    app = CRMApp()
    app.main_menu()
