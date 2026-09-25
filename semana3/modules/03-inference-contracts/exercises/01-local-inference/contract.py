from pydantic import BaseModel, Field
import pandas as pd 

class WineInputSchema(BaseModel):
    sample_id: int = Field(..., description="Unique identifier for the wine sample")
    fixed_acidity: float = Field(..., description="Fixed acidity of the wine sample")
    volatile_acidity: float = Field(..., description="Volatile acidity of the wine sample")
    citric_acid: float = Field(..., description="Citric acid content of the wine sample")
    residual_sugar: float = Field(..., description="Residual sugar content of the wine sample")
    chlorides: float = Field(..., description="Chlorides content of the wine sample")
    free_sulfur_dioxide: float = Field(..., description="Free sulfur dioxide content of the wine sample")
    total_sulfur_dioxide: float = Field(..., description="Total sulfur dioxide content of the wine sample")
    density: float = Field(..., description="Density of the wine sample")
    pH: float = Field(..., description="pH level of the wine sample")
    sulphates: float = Field(..., description="Sulphates content of the wine sample")
    alcohol: float = Field(..., description="Alcohol content of the wine sample")


df = pd.DataFrame.read_csv("wine_data.csv")
for row in df.iterrows():
    