
import logging
from urlparse import urlparse, ParseResult
from allergy_assistant import db

class RecipeWebsiteScraper(object):

    def relative_to_absolute(self, start_path, relative_url):
        """converts a relative url at a specified (absolute) location
        :param: start_path - the absolute path from which the relative url is being accessed
        :param: relative_url - the relative url on the page"""
        parsed_start_url = urlparse(start_path)
        new_path = '/'.join(parsed_start_url.path.split('/')[:-1] + [ relative_url ] )
        parsed_abs_url = ParseResult(scheme=parsed_start_url.scheme, netloc=parsed_start_url.netloc, \
                                path=new_path, params=parsed_start_url.params, query=parsed_start_url.query, \
                                fragment=parsed_start_url.fragment)


        return parsed_abs_url.geturl()


    def remove_extraneous_whitespace(self, string):
       return " ".join(filter(lambda i: not i.isspace(), string.split()))


    def save(self, recipe):
        doc = recipe.format_mongo_doc()
        update_spec = {'_id': doc['_id']}
        db.recipes.update(update_spec, doc, upsert=True)

    def get_recipe_list(self):
        """override me"""
        raise NotImplementedError("Override me!")

    def parse_recipe(self):
        """override me"""
        raise NotImplementedError("Override me!")
    
    def get_all_recipes(self):
        for recipe in self.get_recipe_list():
            try:
                self.parse_recipe(recipe) 
                yield recipe
            except IOError:
                continue

    def get_and_save_all(self):
        if getattr(self, 'ENABLED', False):
            for recipe in self.get_all_recipes():
                self.save(recipe)

    @classmethod
    def get_and_save_all_sources(cls):
        for SiteParser in cls.__subclasses__():
            SiteParser().get_and_save_all()

