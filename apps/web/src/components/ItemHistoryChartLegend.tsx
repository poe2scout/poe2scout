import { FormatTimeFromEpoch } from './FormatTime';
import { BaseCurrencies } from './ReferenceCurrencySelector';
import { UTCTimestamp } from 'lightweight-charts';
import { getCurrencyLabel } from '../currencyMeta';

export interface LegendData {
    price?: number;
    volume?: number;
    time?: UTCTimestamp;
}

export interface ChartLegendProps extends LegendData {
    selectedReference: BaseCurrencies;
    selectedReferenceText?: string;
    textColor?: string; 
}

export const ChartLegend = (props: ChartLegendProps) => {
    const {
        price,
        volume,
        time,
        selectedReference,
        selectedReferenceText,
        textColor = 'white' 
    } = props;

    if (price === undefined && volume === undefined && time === undefined) {
        return null;
    }

    return (
        <div style={{ position: 'absolute', top: 12, left: 75, zIndex: 10, color: textColor, fontFamily: 'sans-serif', fontSize: '14px', pointerEvents: 'none' }}>
            {price !== undefined && (
                <div>
                    <span style={{ color: '#aaa' }}>Price: </span>
                    <strong style={{ color: 'white' }}>{price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>
                    <span style={{ color: '#aaa' }}> {getCurrencyLabel(selectedReference, selectedReferenceText)}</span>
                </div>
            )}
            {volume !== undefined && (
                <div>
                    <span style={{ color: '#aaa' }}>Volume: </span>
                    <strong style={{ color: 'white' }}>{volume.toLocaleString()}</strong>
                </div>
            )}
            {time !== undefined && (
                <div style={{ color: '#aaa', marginTop: '4px' }}>
                    {FormatTimeFromEpoch(time)}
                </div>
            )}
        </div>
    );
};
