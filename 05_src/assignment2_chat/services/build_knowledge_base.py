"""
One-time script to build the ChromaDB food knowledge base.
Run this ONCE before starting the app:

    cd 05_src/assignment2_chat
    python -m services.build_knowledge_base
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import chromadb
from config import get_openai_client, EMBEDDING_MODEL, CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME

# Curated food & nutrition knowledge base
FOOD_KNOWLEDGE = [
    {
        "id": "1",
        "text": "Olive oil is one of the healthiest fats you can consume. Extra virgin olive oil is rich in monounsaturated fatty acids and antioxidants called polyphenols. It has been linked to reduced inflammation, lower cholesterol levels, and improved heart health. It is a staple of the Mediterranean diet.",
        "topic": "nutrition",
    },
    {
        "id": "2",
        "text": "The Maillard reaction is a chemical reaction between amino acids and reducing sugars that gives browned food its distinctive flavor. It occurs at temperatures above 280 F (140 C). This is what makes seared steak, toasted bread, and roasted coffee taste so good. It is different from caramelization, which involves only sugars.",
        "topic": "food_science",
    },
    {
        "id": "3",
        "text": "Fermentation is a metabolic process where microorganisms like yeast and bacteria convert sugars into alcohol, gases, or organic acids. Common fermented foods include yogurt, kimchi, sauerkraut, kombucha, sourdough bread, miso, and tempeh. Fermented foods are beneficial for gut health because they contain probiotics.",
        "topic": "food_science",
    },
    {
        "id": "4",
        "text": "Vitamin C, also known as ascorbic acid, is a water-soluble vitamin found in citrus fruits, strawberries, bell peppers, broccoli, and tomatoes. It is essential for collagen synthesis, immune function, and iron absorption. The recommended daily intake is about 75-90 mg for adults. Cooking can reduce vitamin C content in foods.",
        "topic": "nutrition",
    },
    {
        "id": "5",
        "text": "Gluten is a group of proteins found in wheat, barley, and rye. It gives dough its elastic texture and helps bread rise. People with celiac disease must avoid gluten entirely. Gluten-free alternatives include rice flour, almond flour, coconut flour, and tapioca starch. Oats are naturally gluten-free but are often contaminated.",
        "topic": "nutrition",
    },
    {
        "id": "6",
        "text": "Saffron is the most expensive spice in the world, derived from the stigmas of the Crocus sativus flower. It takes about 75,000 flowers to produce one pound of saffron. It has a distinctive golden color and a complex flavor described as earthy, sweet, and slightly bitter. It is used in dishes like paella, risotto, and bouillabaisse.",
        "topic": "ingredients",
    },
    {
        "id": "7",
        "text": "Umami is the fifth basic taste, alongside sweet, sour, salty, and bitter. It was identified by Japanese chemist Kikunae Ikeda in 1908. Umami is described as a savory, brothy, or meaty taste. Foods rich in umami include parmesan cheese, soy sauce, mushrooms, tomatoes, seaweed, fish sauce, and bone broth. The taste comes from glutamate, an amino acid.",
        "topic": "food_science",
    },
    {
        "id": "8",
        "text": "Sous vide is a cooking technique where food is vacuum-sealed in a bag and cooked in a water bath at a precise, consistent temperature. This method allows for extremely accurate control over doneness. Sous vide was developed in France in the 1970s. It is commonly used for steaks, chicken breasts, eggs, and vegetables.",
        "topic": "cooking_technique",
    },
    {
        "id": "9",
        "text": "Omega-3 fatty acids are essential fats that the body cannot produce on its own. They are found in fatty fish like salmon, mackerel, and sardines, as well as in walnuts, flaxseeds, and chia seeds. Omega-3s are important for brain health, reducing inflammation, and supporting cardiovascular health. The main types are EPA, DHA, and ALA.",
        "topic": "nutrition",
    },
    {
        "id": "10",
        "text": "Blanching is a cooking technique where food is briefly boiled and then immediately plunged into ice water to stop the cooking process. It is used to preserve color, texture, and nutritional value of vegetables. Blanching is also used to loosen the skin of tomatoes and peaches for easy peeling, and to prepare vegetables for freezing.",
        "topic": "cooking_technique",
    },
    {
        "id": "11",
        "text": "Turmeric contains curcumin, a powerful anti-inflammatory and antioxidant compound. It has been used in traditional medicine for thousands of years. Curcumin is poorly absorbed on its own, but combining turmeric with black pepper (which contains piperine) can increase absorption by up to 2000%. Turmeric is a key ingredient in curry powder.",
        "topic": "nutrition",
    },
    {
        "id": "12",
        "text": "Sourdough bread is made using a naturally fermented starter culture instead of commercial yeast. The starter contains wild yeast and lactobacillus bacteria. Sourdough has a lower glycemic index than regular bread, is easier to digest, and has a distinctive tangy flavor. The fermentation process breaks down some of the gluten and phytic acid.",
        "topic": "food_science",
    },
    {
        "id": "13",
        "text": "A mise en place is a French culinary phrase meaning 'everything in its place.' It refers to the practice of preparing and organizing all ingredients before cooking. Professional chefs consider mise en place essential for efficient cooking. It includes washing, chopping, measuring, and arranging ingredients and tools within easy reach.",
        "topic": "cooking_technique",
    },
    {
        "id": "14",
        "text": "Dark chocolate with at least 70% cocoa content is rich in flavonoids, which are powerful antioxidants. Studies suggest that moderate dark chocolate consumption may improve blood flow, lower blood pressure, and reduce the risk of heart disease. Chocolate also contains iron, magnesium, copper, manganese, and small amounts of caffeine and theobromine.",
        "topic": "nutrition",
    },
    {
        "id": "15",
        "text": "The smoke point of an oil is the temperature at which it begins to break down and produce visible smoke. Oils with high smoke points, like avocado oil (520 F), refined peanut oil (450 F), and ghee (485 F), are best for high-heat cooking. Extra virgin olive oil has a moderate smoke point (375 F) and is better for low to medium-heat cooking and dressings.",
        "topic": "cooking_technique",
    },
    {
        "id": "16",
        "text": "Protein is essential for building and repairing tissues, making enzymes and hormones, and supporting immune function. Complete proteins contain all nine essential amino acids and are found in meat, fish, eggs, dairy, quinoa, and soy. The recommended daily protein intake is about 0.8 grams per kilogram of body weight for sedentary adults.",
        "topic": "nutrition",
    },
    {
        "id": "17",
        "text": "Caramelization is the oxidation of sugar when heated above certain temperatures. Table sugar (sucrose) caramelizes at about 340 F (170 C). During caramelization, sugar molecules break down and reform into compounds that create brown color and complex flavors including butterscotch, nutty, and toasty notes. It is not the same as the Maillard reaction.",
        "topic": "food_science",
    },
    {
        "id": "18",
        "text": "The Mediterranean diet emphasizes fruits, vegetables, whole grains, legumes, nuts, seeds, olive oil, and moderate amounts of fish and poultry. It limits red meat, processed foods, and added sugars. Numerous studies have shown it reduces the risk of heart disease, stroke, type 2 diabetes, and certain cancers. It is consistently rated among the healthiest diets in the world.",
        "topic": "nutrition",
    },
    {
        "id": "19",
        "text": "Emulsification is the process of combining two liquids that normally don't mix, like oil and water. An emulsifier acts as a bridge between the two. Egg yolks contain lecithin, a natural emulsifier, which is why they are used in mayonnaise and hollandaise sauce. Mustard and honey are also common emulsifiers in salad dressings.",
        "topic": "food_science",
    },
    {
        "id": "20",
        "text": "Knife skills are fundamental in cooking. The main cuts include: julienne (thin matchstick strips), brunoise (tiny cubes from julienned vegetables), chiffonade (thin ribbons of herbs or leafy greens), mince (very finely chopped), and dice (uniform cubes in small, medium, or large sizes). Proper knife technique improves cooking speed and ensures even cooking.",
        "topic": "cooking_technique",
    },
    {
        "id": "21",
        "text": "Probiotics are live beneficial bacteria found in fermented foods like yogurt, kefir, kimchi, sauerkraut, and miso. They help maintain a healthy gut microbiome, which is linked to improved digestion, immune function, and even mental health. Prebiotics, found in garlic, onions, bananas, and asparagus, serve as food for these beneficial bacteria.",
        "topic": "nutrition",
    },
    {
        "id": "22",
        "text": "Deglazing is a cooking technique where liquid (wine, broth, or vinegar) is added to a hot pan after searing meat or vegetables to loosen the browned bits (fond) stuck to the bottom. These caramelized bits are packed with flavor. Deglazing forms the base for many pan sauces and gravies. It is a technique commonly used in French cuisine.",
        "topic": "cooking_technique",
    },
    {
        "id": "23",
        "text": "Iron is an essential mineral needed for oxygen transport in the blood. Heme iron, found in meat, poultry, and fish, is more easily absorbed than non-heme iron found in plant foods like spinach, lentils, and beans. Vitamin C enhances non-heme iron absorption. Iron deficiency is the most common nutritional deficiency worldwide.",
        "topic": "nutrition",
    },
    {
        "id": "24",
        "text": "Resting meat after cooking allows the juices to redistribute throughout the cut, resulting in a juicier and more flavorful result. During cooking, juices are driven toward the center by heat. If you cut into meat immediately, those juices run out. A general rule is to rest meat for about 5-10 minutes for steaks and 15-20 minutes for roasts.",
        "topic": "cooking_technique",
    },
    {
        "id": "25",
        "text": "Capsaicin is the compound that gives chili peppers their heat. It is measured on the Scoville scale. Bell peppers have 0 Scoville units, jalapenos have 2,500-8,000, habaneros have 100,000-350,000, and the Carolina Reaper can exceed 2 million. Capsaicin has been studied for pain relief, metabolism boosting, and anti-inflammatory properties.",
        "topic": "food_science",
    },
]


def build_knowledge_base():
    """Create embeddings and store them in ChromaDB."""
    print("Building food knowledge base...")

    client = get_openai_client()

    # Get embeddings from OpenAI
    texts = [item["text"] for item in FOOD_KNOWLEDGE]
    print(f"Generating embeddings for {len(texts)} documents...")

    response = client.embeddings.create(
        input=texts,
        model=EMBEDDING_MODEL,
    )

    embeddings = [item.embedding for item in response.data]

    # Store in ChromaDB
    print(f"Storing in ChromaDB at {CHROMA_PERSIST_DIR}...")
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    # Delete collection if it already exists, then recreate
    try:
        chroma_client.delete_collection(name=CHROMA_COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        ids=[item["id"] for item in FOOD_KNOWLEDGE],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"topic": item["topic"]} for item in FOOD_KNOWLEDGE],
    )

    print(f"Knowledge base built! {collection.count()} documents stored.")


if __name__ == "__main__":
    build_knowledge_base()
