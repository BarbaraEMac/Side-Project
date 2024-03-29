"""
Copied from http://code.google.com/p/googleappengine/source/browse/trunk/python/google/appengine/ext/db/__init__.py#3563
"""

import logging
import time

from datetime import timedelta
from google.appengine.api import datastore
from google.appengine.api import memcache, datastore_errors, taskqueue
from google.appengine.ext import db
from google.appengine.datastore import entity_pb
from google.appengine.ext.db import ReferencePropertyResolveError

from util.consts import MEMCACHE_TIMEOUT

_SELF_REFERENCE = object()

class MemcacheReferenceProperty(db.Property):
    """A property that represents a many-to-one reference to another model.

    For example, a reference property in model A that refers to model B forms
    a many-to-one relationship from A to B: every instance of A refers to a
    single B instance, and every B instance can have many A instances refer
    to it.
    """

    def __init__(self, reference_class=None, verbose_name=None, collection_name=None, memcache_key=None, **attrs):
        """Construct MemcacheReferenceProperty.

        Args:
            reference_class: Which model class this property references.
            verbose_name: User friendly name of property.
            collection_name: If provided, alternate name of collection on
                reference_class to store back references.    Use this to allow
                a Model to have multiple fields which refer to the same class.
        """
        super(MemcacheReferenceProperty, self).__init__(verbose_name, **attrs)

        self.collection_name = collection_name
        self.memcache_key = memcache_key

        if reference_class is None:
            reference_class = db.Model
        if not ((isinstance(reference_class, type) and
                         issubclass(reference_class, db.Model)) or
                        reference_class is _SELF_REFERENCE):
            raise KindError('reference_class must be db.Model or _SELF_REFERENCE')

        self.reference_class = self.data_type = reference_class

    def __property_config__(self, model_class, property_name):
        """Loads all of the references that point to this model.

        We need to do this to create the ReverseReferenceProperty properties for
        this model and create the <reference>_set attributes on the referenced
        model, e.g.:

             class Story(db.Model):
                 title = db.StringProperty()
             class Comment(db.Model):
                 story = db.ReferenceProperty(Story)
             story = Story.get(id)
             print [c for c in story.comment_set]

        In this example, the comment_set property was created based on the reference
        from Comment to Story (which is inherently one to many).

        Args:
            model_class: Model class which will have its reference properties
                initialized.
            property_name: Name of property being configured.

        Raises:
            DuplicatePropertyError if referenced class already has the provided
                collection name as a property.
        """
        super(MemcacheReferenceProperty, self).__property_config__(model_class,
                                                                                                             property_name)

        if self.reference_class is _SELF_REFERENCE:
            self.reference_class = self.data_type = model_class

        if self.collection_name is None:
            self.collection_name = '%s_set' % (model_class.__name__.lower())
        existing_prop = getattr(self.reference_class, self.collection_name, None)
        if existing_prop is not None:
            if not (isinstance(existing_prop, db._ReverseReferenceProperty) and
                            existing_prop._prop_name == property_name and
                            existing_prop._model.__name__ == model_class.__name__ and
                            existing_prop._model.__module__ == model_class.__module__):
                raise DuplicatePropertyError('Class %s already has property %s '
                                                                     % (self.reference_class.__name__,
                                                                            self.collection_name))
        setattr(self.reference_class,
                        self.collection_name,
                        db._ReverseReferenceProperty(model_class, property_name))

    def __get__(self, model_instance, model_class):
        """Get reference object.

        This method will fetch unresolved entities from the datastore if
        they are not already loaded.

        Returns:
            ReferenceProperty to Model object if property is set, else None.

        Raises:
            ReferencePropertyResolveError: if the referenced model does not exist.
        """
        instance = None
        #logging.info("FOOOOOO %s %s %s" % (self, model_instance, model_class))

        if model_instance is None:
            return self

        if hasattr(model_instance, self.__id_attr_name()):
            reference_id = getattr(model_instance, self.__id_attr_name())
        else:
            reference_id = None

        if reference_id is not None:
            #logging.info("REference id %s" % reference_id)
            resolved = getattr(model_instance, self.__resolved_attr_name())
            if resolved is not None:
                #logging.info("END: returning resolved")
                #logging.info("END: returning resolved %r" % resolved)
                return resolved
            else:
                logging.info("MemRefProp: memcache key: %s" % self.memcache_key)

                # Check for instance in memcache first
                instance = memcache.get( self.memcache_key )
                
                if instance:
                    #logging.info("Got instance from memcache")
                    # Convert to model from protobuf
                    instance = db.model_from_protobuf(entity_pb.EntityProto(instance))
                
            # Check in DB after checking in memcache
            if not instance:
                #logging.info("Fidning instance in db.")
                instance = db.get(reference_id)

                if instance is None:
                    raise ReferencePropertyResolveError(
                                'ReferenceProperty failed to be resolved: %s' %
                                reference_id.to_path())
            
            if not instance:
                logging.error("END: THIS IS BAD. RETURNING NONE")

            #logging.info("resolved attr name being saved: %s" % (self.__resolved_attr_name()))
            setattr(model_instance, self.__resolved_attr_name(), instance)
            #logging.info("END: returning instance")
            return instance
        else:
            #logging.info("END: returning none")
            return None

    def __set__(self, model_instance, value):
        """Set reference."""

        if not self.memcache_key:
            if isinstance( value, datastore.Key ):
                logging.info("value: %s " % value)
                obj = db.get( value )
                logging.info("OBJ %s" % obj)
                if obj:
                    self.memcache_key = obj.get_key()
                else:
                    self.memcache_key = memcache.get( str( value ) ) 

                logging.info("1: %s" % self.memcache_key)
            elif isinstance( value, db.Model ):
                self.memcache_key = value.get_key() #getattr( value, '_memcache_key', None)
                #logging.info("2: %s" % self.memcache_key)
            else:
                raise TypeError( 'Value supplied is neither <google.appengine.datastore.Key> nor <google.appengine.ext.db.Model>' )
        
        if self.memcache_key is None or self.memcache_key == '':
            logging.error( 'Cannot create memcache key for %s!' % value )
        
        value = self.validate(value)
        if value is not None:
            if isinstance(value, datastore.Key):
                setattr(model_instance, self.__id_attr_name(), value)
                setattr(model_instance, self.__resolved_attr_name(), None)
            else:
                setattr(model_instance, self.__id_attr_name(), value.key())
                setattr(model_instance, self.__resolved_attr_name(), value)
        else:
            setattr(model_instance, self.__id_attr_name(), None)
            setattr(model_instance, self.__resolved_attr_name(), None)

    def get_value_for_datastore(self, model_instance):
        """Get key of reference rather than reference itself."""

        return getattr(model_instance, self.__id_attr_name())

    def validate(self, value):
        """Validate reference.

        Returns:
            A valid value.

        Raises:
            BadValueError for the following reasons:
                - Value is not saved.
                - Object not of correct model type for reference.
        """
        if isinstance(value, datastore.Key):
            return value

        if value is not None and not value.has_key():
            raise BadValueError(
                    '%s instance must have a complete key before it can be stored as a '
                    'reference' % self.reference_class.kind())

        value = super(MemcacheReferenceProperty, self).validate(value)

        if value is not None and not isinstance(value, self.reference_class):
            raise KindError('Property %s must be an instance of %s' %
                                                        (self.name, self.reference_class.kind()))

        return value

    def __id_attr_name(self):
        """Get attribute of referenced id.

        Returns:
            Attribute where to store id of referenced entity.
        """
        return self._attr_name()

    def __resolved_attr_name(self):
        """Get attribute of resolved attribute.

        The resolved attribute is where the actual loaded reference instance is
        stored on the referring model instance.

        Returns:
            Attribute name of where to store resolved reference model instance.
        """
        return '_RESOLVED' + self._attr_name()
