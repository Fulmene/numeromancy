from typing import Iterable

from inflection import singularize

from grammar.DemystifyVisitor import DemystifyVisitor

from mtg_types import Ability, KeywordAbility, KeywordLine, Line, Mana, ManaSymbol, Typeline

def flatten(container: Iterable):
    for i in container:
        if isinstance(i, (list, tuple)):
            yield from flatten(i)
        else:
            yield i

class DemystifyDataVisitor(DemystifyVisitor):

    # Utility methods
    # Visit everything in a context list
    def map_visit(self, ctx):
        if ctx is None:
            return []
        else:
            return list(map(lambda c: self.visit(c), ctx))

    # Terminal
    def visitTerminal(self, node) -> str:
        return singularize(node.getText())


    # Start rule cardManaCost
    def visitCardManaCost(self, ctx) -> Mana:
        return self.visit(ctx.mana())

    def visitMana(self, ctx) -> Mana:
        return self.map_visit(ctx.manaSymbol())

    def visitManaSymbol(self, ctx) -> ManaSymbol:
        return ManaSymbol.from_str(self.visitChildren(ctx))


    # Start rule typeline
    def visitTypeline(self, ctx) -> Typeline:
        supertypes = self.map_visit(ctx.supertype())
        cardTypes = self.map_visit(ctx.cardType())
        subtypes = self.map_visit(ctx.subtype())
        return Typeline(cardTypes, supertypes=supertypes, subtypes=subtypes)


    # Start rule rulesText
    def visitRulesText(self, ctx) -> list[Line]:
        return self.map_visit(ctx.line())

    def visitKeywordLine(self, ctx) -> KeywordLine:
        return self.map_visit(ctx.keywordAbility())

    def visitKeywordAbilityIntCost(self, ctx) -> KeywordAbility:
        return KeywordAbility(
            self.visit(ctx.kw),
            arg_int=None if ctx.keywordArgInt() is None else self.visit(ctx.keywordArgInt()),
            arg_cost=None if ctx.keywordArgCost() is None else self.visit(ctx.keywordArgCost()))

    def visitKeywordAbilityFrom(self, ctx) -> KeywordAbility:
        return KeywordAbility(
            self.visit(ctx.keywordFrom()),
            arg_from=self.map_visit(ctx.keywordArgFrom()))

    def visitKeywordAbilityQuality(self, ctx) -> KeywordAbility:
        return KeywordAbility(
            ctx.kw.text,
            arg_quality=self.visit(ctx.keywordArgQuality()))

    def visitKeywordAbilityQualityCost(self, ctx) -> KeywordAbility:
        return KeywordAbility(
            ctx.kw.text,
            arg_quality=self.visit(ctx.keywordArgQuality()),
            arg_cost=self.visit(ctx.keywordArgCost()))

    def visitAbility(self, ctx) -> Ability:
        effect = self.visit(ctx.spellEffect())
        if ctx.cost() is not None:
            cost = self.visit(ctx.cost())
            return Ability("activated", effect, cost=cost)
        elif ctx.trigger() is not None:
            trigger = self.visit(ctx.trigger())
            return Ability("triggered", effect, trigger=trigger)
        else:
            return Ability("static", effect)


demystify_visitor = DemystifyDataVisitor()
