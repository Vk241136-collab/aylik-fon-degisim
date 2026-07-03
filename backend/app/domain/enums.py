from enum import StrEnum


class ChangeStatus(StrEnum):
    NEW_POSITION = "NEW_POSITION"
    EXITED_POSITION = "EXITED_POSITION"
    WEIGHT_INCREASED = "WEIGHT_INCREASED"
    WEIGHT_DECREASED = "WEIGHT_DECREASED"
    QUANTITY_INCREASED = "QUANTITY_INCREASED"
    QUANTITY_DECREASED = "QUANTITY_DECREASED"
    UNCHANGED = "UNCHANGED"
    RECLASSIFIED = "RECLASSIFIED"
    MATCH_REVIEW_REQUIRED = "MATCH_REVIEW_REQUIRED"


STATUS_LABELS_TR = {
    ChangeStatus.NEW_POSITION: "Yeni alınan",
    ChangeStatus.EXITED_POSITION: "Portföyden çıkan",
    ChangeStatus.WEIGHT_INCREASED: "Ağırlığı artırılan",
    ChangeStatus.WEIGHT_DECREASED: "Ağırlığı azaltılan",
    ChangeStatus.QUANTITY_INCREASED: "Adedi artırılan",
    ChangeStatus.QUANTITY_DECREASED: "Adedi azaltılan",
    ChangeStatus.UNCHANGED: "Değişmeyen",
    ChangeStatus.RECLASSIFIED: "Sınıfı değişen",
    ChangeStatus.MATCH_REVIEW_REQUIRED: "Eşleşmesi kontrol edilmeli",
}


class ParsingStatus(StrEnum):
    UPLOADED = "UPLOADED"
    PARSED = "PARSED"
    FAILED = "FAILED"
    NEEDS_MAPPING = "NEEDS_MAPPING"
