function getNextHourDate(now = new Date()) {
  const nextHour = new Date(now);
  nextHour.setUTCMinutes(0, 0, 0);
  nextHour.setUTCHours(nextHour.getUTCHours() + 1);
  return nextHour;
}

export function getNextHourEndTime(now = new Date()) {
  return getNextHourDate(now).toISOString();
}

export function getNextHourEndEpoch(now = new Date()) {
  return Math.floor(getNextHourDate(now).getTime() / 1000);
}
