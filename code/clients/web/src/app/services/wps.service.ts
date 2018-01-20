import { Injectable } from '@angular/core';
import { WPS } from '../models/WPS';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { catchError, map, tap, switchMap } from 'rxjs/operators';
import { of } from 'rxjs/observable/of';
import { Subscriber } from 'rxjs/Subscriber';
import { WPSProvider } from 'app/models/WPSProvider';

@Injectable()
export class WpsService {
  constructor(private http: HttpClient) { }

  public all(): Observable<WPS[]> {
    return this.http.get<WPS[]>(`https://wpsflow.firebaseio.com/wps.json`);
  }

  public get(id: number): Observable<WPS> {
    return this.http.get<WPS>(`https://wpsflow.firebaseio.com/wps/${id}.json`);
  }

  public create(url: string): Observable<WPS> {
    return this.http.post<WPS>(`https://wpsflow.firebaseio.com/wps.json`, { url });
  }

  public update(id: number, wps: Partial<WPS>): Observable<WPS> {
    return this.http.post<WPS>(`https://wpsflow.firebaseio.com/wps/${id}.json`, { wps });
  }

  public async remove(id: number): Promise<boolean> {
    return this.http.delete<boolean>(`https://wpsflow.firebaseio.com/wps/${id}.json`).toPromise();
  }
}
