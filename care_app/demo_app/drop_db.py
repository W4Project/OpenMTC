#######################################################################
#
# This drops all databases in the MongoDB
#
# Created on June 29, 2023
# @author: Mariel V. Tatel
#
#######################################################################


from pymongo import MongoClient

MONGO_URI = 'mongodb+srv://onem2mCARE1:onem2mCARE1diliman@onem2m.up2wghs.mongodb.net/admin'

def delete_all_database():
    database_list = mongo_client.list_database_names()

    sys_db = ['admin', 'config','local']

    for name in sys_db:
        if name in database_list:
            database_list.remove(name)


    print("Existing database:", *database_list, sep="\n\t")

    to_delete = input("\nAre you sure you want to delete all existing database? [y/n] ")

    if to_delete.lower() == "y":
        print("\nDeleting", len(database_list), "databases...\n")

        for db_name in database_list:
            mongo_client.drop_database(db_name)
            print("Successfully dropped the database:", db_name)
    else:
        print("Not deleting any database.")
        print("Exiting...")


if __name__ == "__main__":

    mongo_client = MongoClient(MONGO_URI, 27017)

    delete_all_database()

    mongo_client.close()

