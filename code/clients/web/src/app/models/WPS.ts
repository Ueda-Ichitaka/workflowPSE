import { WPSProvider } from 'app/models/WPSProvider';

/**
 * wps contains data about a wps server
 */
export interface WPS {
    id: number;
    provider: WPSProvider;
    title: string;
    abstract: string;
}
