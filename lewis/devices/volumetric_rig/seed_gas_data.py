class SeedGasData(object):
    """Contains information about gases and their mixing properties used to set up the initial device state."""

    # Gas names
    unknown = "UNKNOWN"
    empty = "EMPTY"
    vacuum_extract = "VACUUM EXTRACT"
    argon = "ARGON"
    nitrogen = "NITROGEN"
    neon = "NEON"
    carbon_dioxide = "CARBON DIOXIDE"
    carbon_monoxide = "CARBON MONOXIDE"
    helium = "HELIUM"
    gravy = "GRAVY"
    liver = "LIVER"
    hydrogen = "HYDROGEN"
    oxygen = "OXYGEN"
    curried_rat = "CURRIED RAT"
    fresh_coffee = "FRESH COFFEE"
    bacon = "BACON"
    onion = "ONION"
    chips = "CHIPS"
    garlic = "GARLIC"
    brown_sauce = "BROWN SAUCE"

    names = [
        unknown,
        empty,
        vacuum_extract,
        argon,
        nitrogen,
        neon,
        carbon_dioxide,
        carbon_monoxide,
        helium,
        gravy,
        liver,
        hydrogen,
        oxygen,
        curried_rat,
        fresh_coffee,
        bacon,
        onion,
        chips,
        garlic,
        brown_sauce,
    ]

    @staticmethod
    def mixable_gas_names():
        sgd = SeedGasData
        mixable_names = set()
        for g in sgd.names:
            if g not in {sgd.unknown, sgd.liver}:
                mixable_names.add((g, g))
                mixable_names.add((sgd.empty, g))
                mixable_names.add((sgd.vacuum_extract, g))
                mixable_names.add((sgd.argon, g))
                if g != sgd.nitrogen:
                    mixable_names.add((sgd.neon, g))
                    mixable_names.add((sgd.carbon_dioxide, g))
                    if g != sgd.carbon_monoxide:
                        mixable_names.add((sgd.helium, g))
        for g in {sgd.hydrogen, sgd.oxygen, sgd.onion, sgd.garlic, sgd.brown_sauce}:
            mixable_names.add((sgd.gravy, g))
        import itertools

        for pair in list(
            itertools.combinations(
                {
                    sgd.oxygen,
                    sgd.curried_rat,
                    sgd.fresh_coffee,
                    sgd.bacon,
                    sgd.onion,
                    sgd.chips,
                    sgd.garlic,
                    sgd.brown_sauce,
                },
                2,
            )
        ):
            mixable_names.add((pair[0], pair[1]))
        return mixable_names

    @staticmethod
    def buffer_gas_names():
        sgd = SeedGasData
        return [
            (sgd.argon, sgd.argon),
            (sgd.nitrogen, sgd.empty),
            (sgd.neon, sgd.empty),
            (sgd.carbon_dioxide, sgd.empty),
            (sgd.helium, sgd.helium),
            (sgd.hydrogen, sgd.empty),
        ]
