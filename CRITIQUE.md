# First impressions


After cloning and building the containers and following the README.md instructions, I noticed the ```docker compose run --rm app pyright``` command wasn't working.


It should be attributable to some inconsistencies around typing.


The test suite is so tiny, this is expected given the instructions in the README file. We need to improve it.


## General structure


The current directories structure includes:
* data : It includes the sample orders json file. (Potentially we can rename it to test_data, but no huge impact)
* src : The code source files, this is a Python package
* test : It includes a single test file.


We can check the need to create more packages inside src to organize the application code


# Code
## app.py
It seems to be the main file. It is a common name in web development, we can rename it to main.py to be aligned with good practices but it would require also to modify Dockerfile and docker.compose.yml. I will leave this as an optional task.


It contains a single function in charge of:
* Build the path to find the sample data file
* Determine if the sample data file exists or fallback to hardcoded data set
* Call the process data function
* Print out the results


### Recommendations
* Improve the base_dir calculation
* Extract the data dir name and filename to constants to improve legibility
* Write a function to load the data and manage the fallback
   * Use context for file management
   * Use explicit encoding to read the file
   * Use try/except block to catch potential issues with sample data
* Extract fallback data set to a constant
* Write a function to print out the results


## order_service.py
This file contains all the logic to process the orders.


### Recommendations
Most of the improvements are required here:
* OrderDict: Not a great name, we can use a TypedDict to specify the expected keys and types
* We can add an Enum to represent orders status
* handle_orders function
   * Arguments: It is unclear why we need PriorityFlag as an Optional string
   * Output: It can be simplified to a ProcessedOrder List
   * We can simplify this function to receive the orders to process and return the processed list.
   * Return early if input list is empty
   * Not great naming around arguments or the main for loop
   * We need to manage the priority for orders with errors. Maybe set priority to False because we need to fix first the order
   * When executing the app I found the orders were not displayed in the right order based on priority. We need to check the order implementation.


## test_order_service
We need to add the requested tests like:
* Invalid input
* Empty list
* All priority
* All invalid
* Any other edge case I can think


# Further improvements maybe not in the scope
The current project is using pip3 for dependency management.
In larger projects it is recommended to use UV
