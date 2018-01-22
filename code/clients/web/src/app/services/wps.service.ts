import { Injectable } from '@angular/core';
import { WPS } from '../models/WPS';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { catchError, map, tap, switchMap } from 'rxjs/operators';
import { of } from 'rxjs/observable/of';
import { Subscriber } from 'rxjs/Subscriber';
import { WPSProvider } from 'app/models/WPSProvider';
import { MatSnackBar } from '@angular/material';

@Injectable()
export class WpsService {
  constructor(private http: HttpClient, private bar: MatSnackBar) { }

  private getKeyFromId(id: number): Observable<string> {
    return this.http.get<{ [key: string]: WPS }>(`https://wpsflow.firebaseio.com/wps.json`).pipe(
      map(obj => Object.entries(obj).find(([key, wps]) => wps.id === id)),
      map(([key, wps]) => key)
    );
  }

  public all(): Observable<WPS[]> {
    return this.http.get<{ [key: string]: WPS }>(`https://wpsflow.firebaseio.com/wps.json`).pipe(
      map(obj => Object.values(obj))
    );
  }

  public get(id: number): Observable<WPS> {
    return this.getKeyFromId(id).pipe(
      switchMap(key => this.http.get<WPS>(`https://wpsflow.firebaseio.com/wps/${key}.json`))
    );
  }

  public create(url: string): Observable<WPS> {
    console.log('wps creation disabled');
    return null;
    // this.bar.open(`Created WPS`, 'CLOSE', { duration: 3000 });
    // return this.http.post<WPS>(`https://wpsflow.firebaseio.com/wps.json`, wps).pipe(
    //  map(obj => <WPS>wps)
    // );
  }

  public update(id: number, wps: Partial<WPS>): Observable<WPS> {
    this.bar.open(`Saved WPS`, 'CLOSE', { duration: 3000 });
    return this.getKeyFromId(id).pipe(
      switchMap(key => this.http.put<WPS>(`https://wpsflow.firebaseio.com/wps/${key}.json`, wps))
    );
  }

  public async remove(id: number): Promise<boolean> {
    console.log('NICHT LÖSCHEN, Sonst fehlen die Processe');
    this.bar.open(`Deleted WPS`, 'CLOSE', { duration: 3000 });
    return true;
    /*treturn this.getKeyFromId(id).pipe(
      switchMap(key => this.http.delete<boolean>(`https://wpsflow.firebaseio.com/wps/${key}.json`))
    ).toPromise();
    */
  }
}
