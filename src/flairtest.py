import spacy
from flair.data import Sentence
from flair.models import SequenceTagger
from typing import Dict, List

# 1. spaCy pour la segmentation
nlp = spacy.load("en_core_web_sm")

# 2. Flair pour la NER
tagger = SequenceTagger.load('flair/ner-english-large')


def findREN(text: str, entities_by_type: Dict[str, List[str]]):
    doc = nlp(text)

    for sent in doc.sents:
        flair_sentence = Sentence(sent.text)
        tagger.predict(flair_sentence)

        for entity in flair_sentence.get_spans('ner'):
            entity_text = entity.text
            entity_label = entity.tag

            # Filtrer uniquement les entités souhaitées
            if entity_label == 'PER':
                entities_by_type['PERSON'].append(entity_text)
            elif entity_label in ['LOC', 'GPE']:
                entities_by_type['LOC'].append(entity_text)
            elif entity_label == 'ORG':
                entities_by_type['ORG'].append(entity_text)


if __name__ == "__main__":
    text = """Pourtant, ces dernières années, les responsables de la recherche scientifique aux Pays
Bas ont décidé de ne plus soutenir de tels projets de recherche longs et coûteux. La 
première victime en matière éditoriale fut l'édition des actes du Brabant néerlandais : on a 
renoncé aux deux derniers tomes (le Brabant de l'est et du nord-ouest). C'est dans ce 
climat que les éditions informatisées offrent de nouvelles solutions. La production 
d'éditions électroniques coûte moins cher que celle des grandes séries imprimées, et elle 
permet la fourniture de documents provisoires et amendables. Alors une fois abandonné le 
rêve de belles séries imprimées sur les rayons de sa bibliothèque, il paraît raisonnable de 
se consacrer à des éditions numériques qui conviennent mieux aux exigences d'aujourd'hui, 
soit une recherche moins chère et des résultats visibles plus vite. 
Le premier projet de recherche informatisé, présenté ici, semble résulter entièrement 
de ces réflexions négatives. Il s'agit d’offrir une solution au travail déjà réalisé autour des 
actes du Brabant. Une base de données est en constitution, avec les régestes des actes 
déjà réunis. Elle sera publiée sur Internet, sans images. Elle sera gérée par l'Institut pour 
l'Histoire néerlandaise ( Instituut voor Nederlandse Geschiedenis ) à La Haye et les 
Archives d'état au Brabant du Nord ( Rijksarchief in Noord-Brabant) à Bois-le-Duc. 
Un autre projet entièrement nouveau vise l'édition d'un beau fonds bien délimité : celui 
des « schepenkistoorkonden », soit les actes d'échevins conservés dans le « coffre des 
échevins » d'Arnhem. Ce type de conservation des actes d'échevins existe aussi à Kampen 
(Pays-Bas) et à Cologne. Le projet sera aussi dirigé par l'Institut pour l'Histoire 
néerlandaise (Instituut voor Nederlandse Geschiedenis), dans le cadre d'un programme 
d’édition des actes antérieurs à 1300, un programme qui réunit aujourd'hui presque toutes 
les éditions d'actes des Pays-Bas en cours. Cet institut a lancé de nombreuses campagnes 
de numérisation. Le fonds d'Arnhem contient 318 actes, sur parchemin, non scellés, datés 
des années 1293-1348. L'édition prévoit des photographies en couleur, des reproductions 
des notes dorsales, des régestes. 
Mais elle renonce à donner le texte des documents qui reprend indéfiniment le même 
formulaire. Le dernier projet, certainement le plus ambitieux, est aussi le plus avancé. Il 
vise la mise en ligne de tous les actes relatifs aux provinces de Groningen et Drenthe 
jusqu'en 1595, au total environ 20 000 actes. Cette édition remplacera l'édition du XIXe 
siècle 3 et la continuera de l'année 1405 jusqu'à l'année 1595, époque de changements 
politiques et religieux importants. Elle n'est pas gérée par une organisation nationale, mais 
par une fondation régionale (Stichting ùigitaal Oorkondenboek Groningen en Drenthe), 
avec des représentants des archives de Groningen (D. During-Buis et E. Schut), des 
archives et de la province de Drenthe (M. A. W. Gerding et D. H. Huizing) et des 
chercheurs de l'Université de Groningen (J. Hermans, O. Vries, D. E. H. De Boer et """
    entities_by_type = {
        'PERSON': [],
        'LOC': [],
        'ORG': [],
    }

    findREN(text, entities_by_type)

    for label, values in entities_by_type.items():
        print(f"\n{label}:\n", set(values))  # Set pour éviter les doublons
