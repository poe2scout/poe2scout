import { LegendData } from '../ItemHistoryChartLegend';
import { FormatTimeFromEpoch } from '../FormatTime';

export interface PairChartLegendProps extends LegendData {
    currencyOneText?: string;
    currencyTwoText?: string; 
}

export const PairChartLegend = (props: PairChartLegendProps) => {
    const {
        price,
        volume,
        time,
        currencyOneText,
        currencyTwoText
    } = props;

    if (price === undefined && volume === undefined && time === undefined) {
        return null;
    }

    if (window.innerWidth < 500) {
        return null;
    }

    return (
        <div style={{ position: 'absolute', top: 5, left: 10, zIndex: 10, fontFamily: 'sans-serif', fontSize: '14px', pointerEvents: 'none' }}>
            {price !== undefined && (
                <div>
                    <span style={{ color: '#aaa' }}>{currencyOneText} value: </span>
                    <strong style={{ color: 'white' }}>{price.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })} {currencyTwoText}</strong>
                </div>
            )}
            {volume !== undefined && (
                <div>
                    <span style={{ color: '#aaa' }}>{currencyOneText} traded: </span>
                    <strong style={{ color: 'white' }}>{volume.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</strong>
                </div>
            )}
            {time !== undefined && (
                <div style={{ color: '#aaa', marginTop: '4px' }}>
                    {FormatTimeFromEpoch(time as number)}
                </div>
            )}
        </div>
    );
};