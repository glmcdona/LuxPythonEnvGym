'''Implements /src/Game/gen.ts'''



"""
def _generateMap(self):
        '''
        Generate the symmetric random map
        Mirror of /Lux-Design-2021/blob/master/src/logic.ts initialize()->generateGame()
        '''
        seed = random.randint()

        # Generate only part of the map, and apply symettricaly
        symmetry_horizontal = (random.random() <= 0.5)
        half_height = self.height
        half_width = self.width
        if symmetry_horizontal:
            half_height = half_height / 2
        else:
            half_width = half_width / 2

        # DEBUG: Generate some random resources around the map.
        # TODO: Replace with proper symettric map generation after Stone finishes revamp of official generation.
        for x in range(half_height):
            for y in range(half_width):
                if random.rand()  <= 0.10:
                    self.map[y][x].resource = Resource(Constants.RESOURCE_TYPES.WOOD, 400)
                elif random.rand() <= 0.03:
                    self.map[y][x].resource = Resource(Constants.RESOURCE_TYPES.COAL, 100)
                elif random.rand() <= 0.015:
                    self.map[y][x].resource = Resource(Constants.RESOURCE_TYPES.URANIUM, 20)

        # Place the starting cities and workers
        self.game.spawnCityTile(Unit.TEAM.A, 2, 1);
        self.game.spawnCityTile(Unit.TEAM.B, self.width - 3, 1);

        self.game.spawnWorker(Unit.TEAM.A, 2, 2);
        self.game.spawnWorker(Unit.TEAM.B, self.width - 3, 2);
"""