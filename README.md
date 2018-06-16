# Udacity Item Catalog
The Item Catalog project consists of developing an application that provides a list of items. Each item belongs to a specific category. User can browse the descriptions of items. Also it provide a user registration and authentication system. Authenticated users are able to post, edit, or delete their own items.

## Required Software and Environment
- [VirtualBox](https://www.virtualbox.org/)
- [Vagrant](https://www.vagrantup.com/)

## Set Up
1. Install Vagrant and VirtualBox
2. Clone the Udacity Vagrantfile
3. Launch the Vagrant VM `vagrant up`
4. Log into Vagrant VM `vagrant ssh`
4. Browse to the vagrant/catalog directory `cd /vagrant/catalog`

## Use the App
1. Set up database for the app `python database_setup.py`
2. Replace `name`, `email` and `image` of `user_1` in `db_init.py` to your own in order for logging in and CRUD.
3. Initialize database with data `python db_init.py`.
4. Run the application `python views.py`
5. Browse the application in browsers with URL
`http://localhost:5000/`

## JSON Endpoints
- Catalog JSON: `/catalog/JSON`
    
    Display the catalog with all categories and items
- Category JSON: `/catalog/<path:categoryName>/JSON` or `/catalog/<path:categoryName>/items/JSON`

    Display a category with its own items
- Items JSON: `/catalog/items/JSON`
    
    Display all items
- Item JSON: `/catalog/<path:categoryName>/<path:itemName>/JSON`
    
    Display an item
