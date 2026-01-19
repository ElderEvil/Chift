from pydantic import BaseModel, Field


class SyncResult(BaseModel):
    """Schema for sync operation results"""

    inserted: int = Field(default=0, description="Number of records inserted")
    updated: int = Field(default=0, description="Number of records updated")
    deleted: int = Field(default=0, description="Number of records soft-deleted")
    errors: int = Field(default=0, description="Number of errors encountered")
    error_details: list[str] = Field(default_factory=list, description="Detailed error messages")

    def add_error(self, error_msg: str):
        """Add error details"""
        self.errors += 1
        self.error_details.append(error_msg)

    @property
    def total_processed(self) -> int:
        """Total number of records processed"""
        return self.inserted + self.updated + self.deleted

    @property
    def success_rate(self) -> float:
        """Success rate as percentage (0-100)"""
        total = self.total_processed + self.errors
        return (self.total_processed / total * 100) if total > 0 else 0.0

    def __str__(self):
        return f"SyncResult(inserted={self.inserted}, updated={self.updated}, deleted={self.deleted}, errors={self.errors})"


class EntitySyncResult(BaseModel):
    """Schema for individual entity sync result"""

    entity_name: str = Field(description="Name of the entity that was synced")
    result: SyncResult = Field(description="Sync operation results")
    duration_seconds: float = Field(description="Time taken in seconds")

    @property
    def was_successful(self) -> bool:
        """Whether the sync was successful (no critical errors)"""
        return self.result.errors == 0


class FullSyncResult(BaseModel):
    """Schema for complete sync operation results"""

    results: dict[str, SyncResult] = Field(description="Results for each entity type")
    total_duration_seconds: float = Field(description="Total time taken for full sync")
    success_count: int = Field(description="Number of entities successfully synced")
    error_count: int = Field(description="Number of entities with errors")

    @property
    def total_inserted(self) -> int:
        """Total records inserted across all entities"""
        return sum(result.inserted for result in self.results.values())

    @property
    def total_updated(self) -> int:
        """Total records updated across all entities"""
        return sum(result.updated for result in self.results.values())

    @property
    def total_deleted(self) -> int:
        """Total records deleted across all entities"""
        return sum(result.deleted for result in self.results.values())

    @property
    def total_errors(self) -> int:
        """Total errors across all entities"""
        return sum(result.errors for result in self.results.values())

    @property
    def was_successful(self) -> bool:
        """Whether the full sync was completely successful"""
        return self.error_count == 0

    def get_entity_result(self, entity_name: str) -> SyncResult:
        """Get result for a specific entity"""
        return self.results.get(entity_name, SyncResult())
