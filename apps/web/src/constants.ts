export const CURRENCY_TYPES = [
  "currency",
  "ultimatum",
  "breachcatalyst",
  "deliriuminstill",
  "essences",
  "fragments",
  "expedition",
  "ritual",
  "runes",
  "map",
] as const;

export const EQUIPMENT_TYPES = [
  "accessory",
  "armour",
  "flask",
  "jewel",
  "sanctum",
  "weapon",
] as const;

export const CATEGORY_MAPPING: Record<string, string> = {
  currency: "Currency",
  ultimatum: "Ultimatum",
  breachcatalyst: "Breach",
  deliriuminstill: "Delirium",
  essences: "Essences",
  fragments: "Fragments",
  expeditioncurrency: "Expedition Currency",
  waystones: "Waystones",
  runes: "Runes",
  soulcores: "Soul Cores",
  omens: "Omens",
  sanctumrelic: "Sanctum Relic",
  ritual: "Ritual",
  weapon: "Weapon",
  armour: "Armour",
  accessory: "Accessory",
  flask: "Flask",
  jewel: "Jewel",
  sanctum: "Sanctum",
  expedition: "Expedition",
  map: "Maps",
} as const;


