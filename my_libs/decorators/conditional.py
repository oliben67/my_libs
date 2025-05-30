from abc import ABC, abstractmethod
import typing
from pydantic import BaseModel, Field
import inspect

import logging
logging.basicConfig(
    filename="/home/scor/sources/cembalo/cembalo3/conditional.log",
    filemode="a",
    format="%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

class ConditionalProperty(ABC, BaseModel):
    """
    A class property that is only available if the condition is met.
    """

    model_config = {"arbitrary_types_allowed": True}

    condition: typing.Union[typing.Callable[[], bool], str] = Field(
        description="A callable or a string that returns a boolean or a string \
representing the condition.",
    )
    func: typing.Optional[typing.Callable[..., typing.Any]] = Field(
        None,
        description="The function to be decorated.",
        init=False,
    )

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """
        This method should be implemented by subclasses to define the behavior
        of the conditional property.
        It should return the value of the property if the condition is met.
        """
        pass

def generate_descriptor_class(func) -> typing.Type:
    def __get__(_, instance, owner):
        return func(instance)

    return type(f"Descriptor_{func.__name__}", (object,), {"__get__": __get__})

class conditional(type):
    def __new__(mcls, *args, **kwargs):
        # Here we check if the first argument is a class to allow the decorator
        # to be used as a class decorator and pass additional arguments to it
        cls = args[0] if len(args) > 0 else tuple()
        if not inspect.isclass(cls):
            logger.debug("first round")
            mcls.__args__ = args
            mcls.__kwargs__ = kwargs
            return mcls
        logger.debug("second round")
        name = cls.__name__
        bases = (cls,)
        attrs = cls.__dict__.copy()

        # Process conditional properties defined in the class
        conditional_properties = {
            m[0]: m[1] for m in inspect.getmembers(cls) if hasattr(m[1], "__property_decorator__")
        }

        for conditional_property_name, decorated_function in conditional_properties.items():
            # to start with, we --always-- remove the function references from the class
            delattr(cls, conditional_property_name)
            del attrs[conditional_property_name]

            property_decorator = decorated_function.__property_decorator__
            if callable(property_decorator.condition):
                condition_met = property_decorator.condition()
            elif isinstance(property_decorator.condition, str):
                condition_met = eval(property_decorator.condition, {"cls": cls})
            if condition_met:
                if isinstance(property_decorator, conditional.member_property):
                    setattr(cls, conditional_property_name, generate_descriptor_class(decorated_function)())
                    continue
                if isinstance(property_decorator, conditional.class_property):
                    setattr(mcls, conditional_property_name, generate_descriptor_class(decorated_function)())
                    continue

        if issubclass(args[0], BaseModel):
            return cls
        else:
            logger.debug(f"Creating class {name} with bases {bases} and attrs {attrs}")
            return super().__new__(mcls, name, bases, attrs)

    class class_property(ConditionalProperty):
        """
        A --class-- property that is only available if the condition is met.
        """
        def __call__(self, *args, **kwargs):
            if self.func is None:
                func = args[0] if len(args) == 1 else None
                if not callable(func):
                    raise ValueError("Condition must be a callable")
                func.__property_decorator__ = self
                self.func = func
            return self.func

    class member_property(class_property):
        """
        A --member-- property that is only available if the condition is met.
        """
        def __call__(self, *args, **kwargs):
            if self.func is None:
                func = args[0] if len(args) == 1 else None
                if not callable(func):
                    raise ValueError("Condition must be a callable")
                func.__property_decorator__ = self
                self.func = func
            return self.func

import time

test_obj_name = "Boaty McBoatface"

@conditional
class TestingClassTwo():
    def __init__(self):
        self.name = test_obj_name

    @conditional.class_property(condition=lambda: True)
    def conditional_class_property(cls):
        """This property is always available."""
        return f"This class property is always available in {cls.__name__}. [{time.time()}]"

    @conditional.member_property(condition=lambda: True)
    def conditional_member_property(self):
        """This property is always available."""
        return f"This member property is always available in {self}. [{time.time()}]"

    @conditional.member_property(condition=lambda: True)
    def conditional_member_id(self):
        """This property is always available."""
        return id(self)

    @conditional.class_property(condition=lambda: False)
    def unavailable_class_property(cls):
        """This property is never available."""
        return f"This class property is never available in {cls.__name__}. [{time.time()}]"

    @conditional.member_property(condition=lambda: False)
    def unavailable_member_property(self):
        """This property is never available."""
        return f"This member property is never available for {self}. [{time.time()}]"

    @conditional.member_property(condition="False")
    def unavailable_member_property_str_condition(self):
        """This property is never available."""
        return f"This member property is never available for {self}. [{time.time()}]"

    @conditional.member_property(condition="cls.__name__ == 'TestingClassThree'")
    def unavailable_member_property_context_str_condition(self):
        """This property is never available."""
        return f"This member property is never available for {self}. [{time.time()}]"

for i in range(10):
    print(TestingClassTwo.conditional_class_property)
    testing_obj = TestingClassTwo()
    print(testing_obj.conditional_member_property)
    print(f"({testing_obj.conditional_member_id == id(testing_obj)})")
    print(hasattr(TestingClassTwo, "unavailable_class_property"), False)
    print(hasattr(TestingClassTwo(), "unavailable_member_property"), False)
    print(hasattr(TestingClassTwo(), "unavailable_member_property_str_condition"), False)
    print(hasattr(TestingClassTwo(), "unavailable_member_property_context_str_condition"), False)
    time.sleep(1)
