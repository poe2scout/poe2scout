import { formatDistanceToNow, fromUnixTime } from "date-fns";
import { formatInTimeZone } from "date-fns-tz";


export function FormatTime(date: Date): String{
    const absoluteTime = formatInTimeZone(date, 'UTC', "dd MMM yyyy, HH:mm 'UTC'");
    const relativeTime = formatDistanceToNow(date, { addSuffix: true });

    return `${absoluteTime} (${relativeTime})`
}

export function FormatTimeFromEpoch(epoch: number): String{
    const date = fromUnixTime(epoch as number);

    const absoluteTime = formatInTimeZone(date, 'UTC', "dd MMM yyyy, HH:mm 'UTC'");
    const relativeTime = formatDistanceToNow(date, { addSuffix: true });

    return `${absoluteTime} (${relativeTime})`
}