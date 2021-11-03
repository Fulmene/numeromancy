from typing import Iterable
from inflection import singularize

from grammar.DemystifyParser import DemystifyParser
from grammar.DemystifyVisitor import DemystifyVisitor

from .types import Mana, ManaSymbol, Typeline, RulesText

class DemystifyDataVisitor(DemystifyVisitor):

    # Utility methods

    # Visit everything in a context list
    def map_visit(self, ctx):
        return list(map(lambda c: self.visit(c), ctx))


    # Get text from context with a single leaf node, singularized
    def get_text(self, ctx):
        return singularize(ctx.getChild(0).getText())


    # Start rule cardManaCost
    def visitCardManaCost(self, ctx):
        return self.visit(ctx.mana())


    def visitMana(self, ctx) -> Mana:
        return self.map_visit(ctx.manaSymbol())


    def visitManaSymbol(self, ctx) -> ManaSymbol:
        return ManaSymbol.from_str(self.get_text(ctx))


    # Start rule typeline
    def visitTypeline(self, ctx):
        supertypes = self.visit(ctx.supertypes()) if ctx.supertypes() != None else []
        cardTypes = self.visit(ctx.cardTypes())
        subtypes = self.visit(ctx.subtypes()) if ctx.subtypes() != None else []
        return Typeline(cardTypes, supertypes=supertypes, subtypes=subtypes)


    def visitSupertypes(self, ctx):
        return self.map_visit(ctx.supertype())


    def visitSupertype(self, ctx):
        return self.get_text(ctx)


    def visitCardTypes(self, ctx):
        return self.map_visit(ctx.cardType())


    def visitCardType(self, ctx):
        return self.get_text(ctx)


    def visitSubtypes(self, ctx):
        return self.map_visit(ctx.subtype())


    def visitSubtype(self, ctx):
        return self.get_text(ctx)


    # Start rule rulesText
    def visitRulesText(self, ctx):
        return RulesText(self.map_visit(ctx.line()))


    def visitLine(self, ctx):
        return self.visit(ctx.getChild(0))


    def visitKeywordLine(self, ctx):
        return self.map_visit(ctx.keywordAbility())


    def visitAbility(self, ctx):
        return self.visit(ctx.getChild(0))



