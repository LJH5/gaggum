import { atom } from "recoil";

export let needWaterState = atom({
  key: "needWaterState",
  default: null,
});

export let weatherState = atom({
  key: "weatherState",
  default: null,
});

export let doLocationState = atom({
  key: "doLocationState",
  default: null,
});

export let guLocationState = atom({
  key: "guLocationState",
  default: null,
});

export let getAllPlantListState = atom({
  key: "getAllPlantList",
  default: null,
});

export let getPlantDetailState = atom({
  key: "getPlantDetailState",
  default: null,
});

export let socketState = atom({
  key: "socketState",
  default: null,
});

export let socketState2 = atom({
  key: "socketState2",
  default: null,
});
