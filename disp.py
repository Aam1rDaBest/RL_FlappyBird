import inspect


class MyClass:
    def call(self):
        self.ring()

    def call1(self):
        self.ring()

    def ring(self):
        # Get the call stack
        stack = inspect.stack()

        # Print information about each frame in the stack
        for frame_info in stack:
            frame = frame_info.frame
            function_name = frame.f_code.co_name
            line_number = frame.f_lineno
            filename = frame.f_code.co_filename
            print(f" Function: {function_name}")


# Create an instance of MyClass
my_obj = MyClass()

# Call the call method
my_obj.call()
print("done")
# Call the call1 method
my_obj.call1()
