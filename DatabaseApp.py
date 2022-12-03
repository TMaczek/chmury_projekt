from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable


# wiekszosc fukcji działa parami - dostępna przez api i statyczna
# opisane sa funkcje dostepne, statyczne uzupelniaja ich dzialanie
# funkcja 'do pary' jest zaraz po pierwszej

class DatabaseApp:

    def __init__(self, uri, user, password):
        """
        Tworzenie instancji klasy, łaczy z bazą
        :param uri: url bazy
        :param user: nazwa użytkownika
        :param password: hasło
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Zamnknięcie połączenia z bazą.
        """
        self.driver.close()

    def check_if_exists(self, character_name, node_type):
        """
        Spradzenie czy node o danej nazwie istnieje w bazie
        :param character_name: atrybut name
        :param node_type: typ node'a
        :return: ilosc znalezionych node'ow
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._check_if_exists, character_name, node_type)
            return result

    @staticmethod
    def _check_if_exists(tx, character_name, node_type):
        query = (
         "MATCH (p: " + node_type + ") WHERE p.name=$character_name RETURN p"
        )
        result = tx.run(query, character_name=character_name)
        return len(result.data())

    def check_if_exists_relation(self, node1, node2, name1, name2, rel):
        """
        Sprawdza czy istnieje relacja
        :param node1: name 1szego node'a
        :param node2: name 2giego node'a
        :param name1: typ 1szego node'a
        :param name2: typ 2giego node'a
        :param rel: typ relacji
        :return: ilosc takich relacji
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._check_if_exists_relation, node1, node2, name1, name2, rel)
            return result[0]['res']

    @staticmethod
    def _check_if_exists_relation(tx, node1, node2, name1, name2, rel):
        query = (
         "MATCH ( a: " + name1 + " ) -[ r: " + rel+" ] - (b: " + name2 + " ) "
         "WHERE a.name = '" + node1+"'  AND b.name= '" + node2 + "' return count(r) as res"
        )
        result = tx.run(query)
        return result.data()

    def check_if_fusion(self, name):
        """
        Sprawdza czy postac o danym imieniu jest fuzją
        :param name: nazwa postaci
        :return: 0 jesli nie jest, inna wartosc jesli jest
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._check_if_fusion, name)
            return result[0]['res']

    @staticmethod
    def _check_if_fusion(tx, name):
        query = (
         "MATCH (f:Character) -[r:FUSION_OF] -> (c:Character) WHERE f.name=$name return count(r) as res"
        )
        result = tx.run(query, name=name)
        return result.data()

    def add_generic(self, character_name, node_type):
        """
        Generyczna funkcja dodajaca wezel
        :param character_name: nazwa wezla
        :param node_type: typ wezla
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._add_and_return, character_name, node_type)
            for row in result:
                print("Added  {node} : {p}".format(p=row['p'], node=node_type))

    @staticmethod
    def _add_and_return(tx, character_name, node_type):
        query = (
         "CREATE (p: " + node_type + " { name: $character_name }) "
         "RETURN p"
        )
        result = tx.run(query, character_name=character_name)
        try:
            return [{"p": row["p"]["name"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def add_episode(self, name, season, number, overall):
        """
        Funkcja dodajaca odcinek
        :param name: nazwa odcinka
        :param season: numer sezonu
        :param number: numer w sezonie
        :param overall: numer dla calosci
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._add_and_return_episode, name, season, number, overall)
            for row in result:
                print("Added episode: {p}".format(p=row['p']))

    @staticmethod
    def _add_and_return_episode(tx, name, season, number, overall):
        query = (
         "CREATE (p: Episode { name: $name, season: $season, number: $number, overall: $overall }) "
         "RETURN p"
        )
        result = tx.run(query, name=name, season=int(season), number=int(number), overall=int(overall))
        try:
            return [{"p": row["p"]["name"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def add_characters(self, *character_names):
        """
        Dodaje 1 lub wiecej postaci
        :param character_names: nazwy postaci
        """
        for character_name in character_names:
            self.add_generic(character_name, "Character")

    def add_groups(self, *group_names):
        """
        Dodaje 1 lub wiecej grup
        :param group_names: nazwy grupy
        """
        for group_name in group_names:
            self.add_generic(group_name, "Group")

    def add_writers(self, *writer_names):
        """
        Dodaje 1 lub wiecej writerow
        :param writer_names: nazwy writerow
        """
        for writer_name in writer_names:
            self.add_generic(writer_name, "Writer")

    def delete_by_name(self, name):
        """
        Usuwa node o nazwie
        :param name: name node'a do usuniecia
        """
        with self.driver.session(database="neo4j") as session:
            session.execute_write(self._delete_by_name, name)

    @staticmethod
    def _delete_by_name(tx, name):
        query = (
            "MATCH (n {name: $name}) DETACH DELETE n "
        )
        tx.run(query, name=name)

    def delete_relation_between(self, a, b):
        """
        Usuwa dowolna relacje miedzy node'ami
        :param a: name 1szego node'a
        :param b: name 2giego node'a
        """
        with self.driver.session(database="neo4j") as session:
            session.execute_write(self._delete_relation_between, a, b)

    @staticmethod
    def _delete_relation_between(tx, a, b):
        query = (
            "MATCH (a)-[r]-(b) WHERE a.name=$a and b.name=$b DELETE r  "
        )
        tx.run(query, a=a, b=b)

    def delete_everything(self):
        """
        Niebezpieczna funkcja - usuwa wszystko z bazy
        """
        with self.driver.session(database="neo4j") as session:
            session.execute_write(self._delete_everything)
            print("Database cleaned, it should be empty now")

    @staticmethod
    def _delete_everything(tx):
        query = (
            "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n, r"
        )
        tx.run(query)

    def add_constraints(self):
        """
        Dodaje constrainty do bazy
        """
        with self.driver.session(database="neo4j") as session:
            session.execute_write(self._add_constraints)
            print("Constraint added")

    @staticmethod
    def _add_constraints(tx):
        queries = [
            "CREATE CONSTRAINT character_name FOR (c:Character) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT group_name FOR (g:Group) REQUIRE g.name IS UNIQUE",
            "CREATE CONSTRAINT writer_name FOR (w:Writer) REQUIRE w.name IS UNIQUE",
            "CREATE CONSTRAINT episode_name FOR (e:Episode) REQUIRE e.name IS UNIQUE",
            "CREATE CONSTRAINT episode_overall FOR (e:Episode) REQUIRE e.overall IS UNIQUE"
        ]
        for query in queries:
            tx.run(query)

    def add_generic_relation(self, from_where, to_where, what_kind, from_node, to_node):
        """
        Generyczna funkcja do dodawania relacji
        :param from_where: name node'a startowego
        :param to_where: name node'a koncowego
        :param what_kind: typ relacji
        :param from_node: typ node'a startowego
        :param to_node: typ node'a koncowego
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self._add_and_return_generic_relation, from_where, to_where, what_kind, from_node, to_node)
        for row in result:
            print("Added : {a} - {rel} -> {b}".format(a=row['a'], b=row['b'], rel=what_kind))

    @staticmethod
    def _add_and_return_generic_relation(tx, from_where, to_where, what_kind, from_node, to_node):
        query = (
            "MATCH (a:" + from_node + ") WHERE a.name=$from_where  "
            "MATCH (b:" + to_node + ") WHERE b.name=$to_where "
            "CREATE (a)-[:" + what_kind + "]->(b) "
            "RETURN a, b"
           )
        result = tx.run(query, from_where=from_where, to_where=to_where)
        try:
            return [{"a": row["a"]["name"], "b": row["b"]["name"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def add_wrote(self, episode,  *writers):
        """
        Dodaje writera/ow do danego odcinka
        :param episode: nazwa odcinka
        :param writers: 1 lub wiecej writerow
        """
        for writer in writers:
            self.add_generic_relation(writer, episode, "WROTE", "Writer", "Episode")

    def add_appeared(self, episode, *characters, ):
        """
        Dodaje do odcinka postacie ktore sie w nim pojawily
        :param episode: nazwa odcinka
        :param characters: 1 lub wiecej postaci
        """
        for character in characters:
            self.add_generic_relation(character, episode, "APPEARED_IN", "Character", "Episode")

    def add_belongs_to(self, group, *characters):
        """
        Dodaje do grupy postacie
        :param group: nazwa grupy
        :param characters: 1 lub wiecej postaci
        """
        for character in characters:
            self.add_generic_relation(character, group, "BELONGS_TO", "Character", "Group")

    def add_fusion_of(self, fusion, *characters):
        """
        Tworzy fuzje z postaci
        :param fusion: nazwa fuzji
        :param characters: postacie wchodzace w fuzje
        """
        for character in characters:
            self.add_generic_relation(fusion, character, "FUSION_OF", "Character", "Character")

    def get_episodes(self):
        """
        Pobiera wszystkie odcinki z bazy
        :return: tablica dictionarow z danymi odcinkow
        """
        with self.driver.session(database="neo4j") as session:
            results = session.execute_read(self._get_episodes)
            return results

    @staticmethod
    def _get_episodes(tx):
        query = (
            "MATCH (e:Episode) return e ORDER BY e.overall"
        )
        result = tx.run(query)
        results = [{'overall': record['e'].get('overall'),
                    'name': record['e'].get('name'),
                    'season':record['e'].get('season'),
                    'number': record['e'].get('number')} for record in result.data()]
        return results

    def get_characters(self):
        """
        Pobiera dane postaci z bazy
        :return: tablica z nazwami postaci
        """
        with self.driver.session(database="neo4j") as session:
            results = session.execute_read(self._get_characters)
            return results

    @staticmethod
    def _get_characters(tx):
        query = (
            "MATCH (c:Character) return c "
        )
        result = tx.run(query)
        results = [{'name': record['c'].get('name')} for record in result.data()]
        return results

    def get_writers(self):
        """
        Pobiera dane writerow z bazy
        :return: tablica z nazwami writerow
        """
        with self.driver.session(database="neo4j") as session:
            results = session.execute_read(self._get_writers)
            return results

    @staticmethod
    def _get_writers(tx):
        query = (
            "MATCH (w:Writer) return w "
        )
        result = tx.run(query)
        results = [{'name': record['w'].get('name')} for record in result.data()]
        return results

    def get_groups(self):
        """
        Pobiera dane grup z bazy
        :return: tablica z nazwami grup
        """
        with self.driver.session(database="neo4j") as session:
            results = session.execute_read(self._get_groups)
            return results

    @staticmethod
    def _get_groups(tx):
        query = (
            "MATCH (g:Group) return g "
        )
        result = tx.run(query)
        results = [{'name': record['g'].get('name')} for record in result.data()]
        return results

    def get_fusions(self):
        """
        Pobiera wszystkie fuzje z bazy
        :return: tablica z nazwami fuzji
        """
        with self.driver.session(database="neo4j") as session:
            results = session.execute_read(self._get_fusions)
            return results

    @staticmethod
    def _get_fusions(tx):
        query = (
            "MATCH (c:Character) -[r:FUSION_OF] -> () RETURN DISTINCT c"
        )
        result = tx.run(query)
        results = [{'name': record['c'].get('name')} for record in result.data()]
        return results

    def find_characters_episodes(self, character_name):
        """
        Znajduje wszystkie odcinki postaci
        :param character_name: nazwa postaci
        :return: tablica z danymi odcinkow
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(self._find_and_return_characters_episodes, character_name)
            return result

    @staticmethod
    def _find_and_return_characters_episodes(tx, character_name):
        query = (
            "MATCH (c:Character) -[r:APPEARED_IN] -> (e:Episode) WHERE c.name=$character_name RETURN e as name "
        )
        result = tx.run(query, character_name=character_name)
        return [row["name"] for row in result]

    def find_fusion_parts(self, character_name):
        """
        Znajduje elementy fuzji postaci
        :param character_name: nazwa fuzji
        :return: tablica z danymi czesci tej fuzji
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(self._find_and_return_fusion_parts, character_name)
            return result

    @staticmethod
    def _find_and_return_fusion_parts(tx, character_name):
        query = (
            "MATCH (c:Character) -[r:FUSION_OF] -> (f:Character) WHERE c.name = $character_name RETURN f "
        )
        result = tx.run(query, character_name=character_name)
        return [row['f'].get('name') for row in result.data()]

    def find_character_data(self, character_name):
        """
        Znajduje i zwraca dane postaci tj grupy i odcinki
        :param character_name: nazwa postaci
        :return: tablica grup, tablica odcinkow
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(self._find_and_return_character_data, character_name)
            return result

    @staticmethod
    def _find_and_return_character_data(tx, character_name):
        query = (
            "MATCH (c:Character) -[r:BELONGS_TO] - (g:Group) "
            "WHERE c.name=$character_name "
            "RETURN g"
        )
        result = tx.run(query, character_name=character_name)
        groups = [{'group': record['g'].get('name')}for record in result.data()]
        query2 = (
            "MATCH (c:Character) -[r:APPEARED_IN] - (e:Episode) "
            "WHERE c.name=$character_name "
            "RETURN e ORDER BY e.overall"
        )
        result2 = tx.run(query2, character_name=character_name)
        episodes = [{'episode': record['e'].get('name')} for record in result2.data()]
        return groups, episodes

    def find_episode_data(self, episode_name):
        """
        Znajduje dane odcinka, jego writerow i postacie w nim
        :param episode_name: nazwa odcinka
        :return: dane odcinka, postacie, writerzy
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(self._find_and_return_episode_data, episode_name)
            return result

    @staticmethod
    def _find_and_return_episode_data(tx, episode_name):
        query = (
            "MATCH (e:Episode) "
            "WHERE e.name=$episode_name "
            "RETURN e"
        )
        result = tx.run(query, episode_name=episode_name)
        record = (result.data()[0])
        episode = {'name': record['e'].get('name'),
                   'number': record['e'].get('number'),
                   'season': record['e'].get('season'),
                   'overall': record['e'].get('overall')}
        query2 = (
            "MATCH (c:Character) -[r:APPEARED_IN] - (e:Episode) "
            "WHERE e.name=$episode_name "
            "RETURN c"
        )
        result2 = tx.run(query2, episode_name=episode_name)
        characters = [{'character': record['c'].get('name')} for record in result2.data()]
        query3 = (
            "MATCH (w:Writer) -[wr:WROTE] -> (e:Episode) "
            "WHERE e.name=$episode_name "
            "return w"
        )
        result3 = tx.run(query3, episode_name=episode_name)
        writers = [{'writer': record['w'].get('name')} for record in result3.data()]
        return episode, characters, writers

    def find_writer_data(self, writer_name):
        """
        Znajduje odcinki napisane przez writera
        :param writer_name: nazwa writera
        :return: odcinki
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(self._find_and_return_writer_data, writer_name)
            return result

    @staticmethod
    def _find_and_return_writer_data(tx, writer_name):
        query = (
            "MATCH (w:Writer) -[wr:WROTE] -> (e:Episode)"
            "WHERE w.name=$writer_name "
            "return e ORDER BY e.overall "

        )
        result = tx.run(query, writer_name=writer_name)
        episodes = [{'episode': record['e'].get('name')}for record in result.data()]
        return episodes

    def find_group_data(self):
        """
        Znajduje wszystkie grupy i zwraca je wraz z ich czlonkami
        :return: nazwy grup + ich czlonkowie
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(self._find_and_return_groups_data)
            return result

    @staticmethod
    def _find_and_return_groups_data(tx):
        query = (
            "MATCH (g:Group) return g"
        )
        result = tx.run(query)
        groups = [{'name': record['g'].get('name')} for record in result.data()]
        members = {}
        for group in groups:
            name = group['name']
            query = (
                "MATCH (c:Character) -[r:BELONGS_TO] - (g:Group) WHERE g.name=$name return c"
            )
            result = tx.run(query, name=name)
            mem = [{'name': record['c'].get('name')} for record in result.data()]
            members[str(name)] = mem
        return groups, members

    def add_series_data(self):
        """
        Dodaje przykladowe dane do tabeli
        """
        self.delete_everything()
        self.add_constraints()
        self.add_characters("Steven", "Garnet", "Amethyst", "Pearl", "Lars", "Sadie", "Lion",
                            "Opal", "Sugilite", "Greg", "Connie", "Ruby", "Sapphire", "Jasper",
                            "Peridot", "Lapis", "Sardonyx", "Stevonnie", "Yellow Diamond",
                            "Blue Diamond")

        self.add_writers("Joe Johnston", "Jeff Liu", "Lamar Abrams", "Aleth Romanillos", "Raven Molisee",
                         "Paul Villeco", "Hillary Florido", "Jesse Zuko", "Colin Howard", "Takafumi Hori",
                         "Katie Mitroff")

        self.add_fusion_of("Stevonnie", "Steven", "Connie")
        self.add_fusion_of("Garnet", "Ruby", "Sapphire")
        self.add_fusion_of("Opal", "Pearl", "Amethyst")
        self.add_fusion_of("Sugilite", "Garnet", "Amethyst")
        self.add_fusion_of("Sardonyx", "Pearl", "Garnet")

        self.add_groups("Crystal Gems", "Beach City", "Homeworld")
        self.add_belongs_to("Crystal Gems", "Steven", "Garnet", "Amethyst", "Pearl")
        self.add_belongs_to("Beach City", "Steven", "Greg", "Lars", "Sadie")
        self.add_belongs_to("Homeworld", "Yellow Diamond", "Blue Diamond", "Jasper", "Peridot", "Lapis")

        self.add_episode("Gem Glow", 1, 1, 1)
        self.add_appeared("Gem Glow", "Steven", "Garnet", "Amethyst", "Pearl", "Lars", "Sadie")
        self.add_wrote("Gem Glow", "Joe Johnston", "Jeff Liu")

        self.add_episode("Steven's Lion", 1, 10, 10)
        self.add_appeared("Steven's Lion", "Steven", "Garnet", "Amethyst", "Pearl", "Lion")
        self.add_wrote("Steven's Lion", "Lamar Abrams", "Aleth Romanillos")

        self.add_episode("Lion 2: The Movie", 1, 17, 17)
        self.add_appeared("Lion 2: The Movie", "Steven", "Garnet", "Amethyst", "Pearl", "Lion", "Connie")
        self.add_wrote("Lion 2: The Movie", "Joe Johnston", "Jeff Liu")

        self.add_episode("Giant Woman", 1, 12, 12)
        self.add_appeared("Giant Woman", "Steven", "Garnet", "Amethyst", "Pearl", "Opal")
        self.add_wrote("Giant Woman", "Joe Johnston", "Jeff Liu")

        self.add_episode("Coach Steven", 1, 20, 20)
        self.add_appeared("Coach Steven", "Steven", "Garnet", "Amethyst", "Pearl", "Sugilite", "Greg", "Lars", "Sadie")
        self.add_wrote("Coach Steven", "Raven Molisee", "Paul Villeco")

        self.add_episode("Cry for Help", 2, 11, 63)
        self.add_appeared("Cry for Help", "Steven", "Garnet", "Amethyst", "Pearl", "Sugilite", "Sardonyx")
        self.add_wrote("Cry for Help", "Joe Johnston", "Jeff Liu")

        self.add_episode("Gem Drill", 3, 2, 80)
        self.add_appeared("Gem Drill", "Steven", "Peridot")
        self.add_wrote("Gem Drill", "Raven Molisee", "Paul Villeco")

        self.add_episode("Barn Mates", 3, 4, 82)
        self.add_appeared("Barn Mates", "Steven", "Peridot", "Lapis")
        self.add_wrote("Barn Mates", "Hillary Florido", "Jesse Zuko")

        self.add_episode("Mr. Greg", 3, 8, 86)
        self.add_appeared("Mr. Greg", "Steven", "Greg", "Pearl")
        self.add_wrote("Mr. Greg", "Joe Johnston", "Jeff Liu")

        self.add_episode("Mindful Education", 4, 4, 107)
        self.add_appeared("Mindful Education", "Steven", "Connie", "Garnet", "Stevonnie", "Pearl")
        self.add_wrote("Mindful Education", "Colin Howard", "Jeff Liu", "Takafumi Hori")

        self.add_episode("Lion 4: Alternate Ending", 4, 21, 124)
        self.add_appeared("Lion 4: Alternate Ending", "Steven", "Lion", "Greg")
        self.add_wrote("Lion 4: Alternate Ending", "Hillary Florido", "Paul Villeco")

        self.add_episode("The Trial", 5, 2, 130)
        self.add_appeared("The Trial", "Steven", "Lars", "Yellow Diamond", "Blue Diamond")
        self.add_wrote("The Trial", "Katie Mitroff", "Paul Villeco")

        self.add_episode("Escapism", 5, 28, 156)
        self.add_appeared("Escapism", "Steven", "Connie", "Stevonnie", "Lion")
        self.add_wrote("Escapism", "Joe Johnston", "Jeff Liu")
