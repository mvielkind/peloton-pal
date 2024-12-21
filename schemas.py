from typing import Optional
from pydantic import BaseModel, Field


class UserWorkoutPreferences(BaseModel):
    fitness_goals: list[str] = Field(default=None, description="Array of fitness goals for the user. Ordered by the priority of importance.")
    preferred_intensity: Optional[str] = Field(default=None, description="User's preferred intensity range on a scale of 0-10 where 0 is lowest intensity and 10 is highest intensity")
    preferred_duration_minutes: int = Field(default=30, description="Number of minutes a workout duration should be.")
    excluded_classes: list[str] = Field(default=None, description="Types of classes the user does not wanted included in their workout.")
    favorite_instructors: list[str] = Field(default=None, description="Names of the user's favorite instructors.")


class RecentUserSummary(BaseModel):
    recent_class_ids: list[str] = Field(description="List of class IDs for the recent user classes.")
    summary: str = Field(description="Analysis of the user's recent workouts and how they align with fitness goals.")


class RecentUserClasses(BaseModel):
    id: str = Field(description="ID of the class.")
    fitness_discipline: str = Field(description="Category the class is assigned to (cardio, strength, cycling etc.)")
    name: str = Field(description="Name of the class")
    class_date: str = Field(description="Date the user took the class.")
    description: str = Field(description="Brief description of the class.")
    title: str = Field(description="Display title for the class")
    instructor: str = Field(description="Name of the class instructor")


class PelotonClass(BaseModel):
    id: str = Field(description="ID of the class")
    title: str = Field(description="Display title for the class")
    description: str = Field(description="Brief description of the class")
    duration: int = Field(description="Duration of the class measured in minutes.")
    difficulty: float = Field(description="Class difficulty on a scale of 0-10 where 0 is easy and 10 is the most difficult.")
    fitness_discipline: str = Field(description="Category the class is assigned to (cardio, strength, cycling etc.)")
    instructor: str = Field(description="Name of the class instructor")
