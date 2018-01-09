import { WPSProvider } from 'app/models/WPSProvider';

export interface WPS {
    id: number;
    provider: WPSProvider;
    title: string;
    abstract: string;
}
