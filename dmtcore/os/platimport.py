import logging
from dmtcore.os.platinfo import get_os_name

module_logger = logging.getLogger("dmtcore.os.platimport")


def platimport(parent_module, property_name, submodule = None):
    """
    Imports a property (attr, function, class) from an indicated module according to the
    platform where the application is being run.
    
    :param parent_module: The name of the parent module 
    :param property_name: The name of the property to import from the platform module
    :param submodule: If the property lives in a submodule, indicate it's name to import from it
    :type parent_module: string
    :type property_name: string
    :type submodule: string
    
    Example:
    
    To import parent.module.<platform>.property
    >>> platimport("parent.module", "property")
    
    To import parent.module.<platform>.submodule.property
    >>> platimport("parent.module", "property", submodule = "submodule")
    """
    submodule_str = "" if submodule is None else ".%s" % submodule
    os_name = get_os_name()
    d = {"parent_module": parent_module, "platform": os_name, "submodule_str": submodule_str}
    platform_module = "{parent_module}.{platform}{submodule_str}".format(**d)
    
    try:
        module_logger.info("Trying to import property {0} from module \
                                {1}".format(property_name, platform_module))
        module = __import__(platform_module, globals(), locals(), [""])
        return getattr(module, property_name)
    except ImportError:
        module_logger.error("Import error of module {0}".format(module))
        raise NotImplementedError("Error while importing. Is {0} supported/implemented?".format(os_name))
    except AttributeError:
        module_logger.error("Error getting property {0} from module {1}".format(property_name, module))
        raise NotImplementedError("Error while getting property {0}.\
                Is it supported/implemented for {1}?".format(property_name, os_name))        
        