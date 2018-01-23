import { Injectable } from '@angular/core';
import { WPS } from '../models/WPS';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { map, switchMap } from 'rxjs/operators';
import { MatSnackBar } from '@angular/material';

@Injectable()
export class WpsService {
  /**
   * Constructs wps service
   * @param {HttpClient} http
   * @param {MatSnackBar} bar
   */
  constructor(private http: HttpClient, private bar: MatSnackBar) { }

  /**
   * Returns key
   * @param {number} id
   * @returns {Observable<string>}
   */
  private getKeyFromId(id: number): Observable<string> {
    return this.http.get<{ [key: string]: WPS }>(`https://wpsflow.firebaseio.com/wps.json`).pipe(
      map(obj => Object.entries(obj).find(([key, wps]) => wps.id === id)),
      map(([key, wps]) => key)
    );
  }

  /**
   * Returns an observable to all WPS
   * @returns {Observable<WPS[]>}
   */
  public all(): Observable<WPS[]> {
    return this.http.get<{ [key: string]: WPS }>(`https://wpsflow.firebaseio.com/wps.json`).pipe(
      map(obj => Object.values(obj))
    );
  }

  /**
   * Return WPS with given id
   * @param {number} id
   * @returns {Observable<WPS>}
   */
  public get(id: number): Observable<WPS> {
    return this.getKeyFromId(id).pipe(
      switchMap(key => this.http.get<WPS>(`https://wpsflow.firebaseio.com/wps/${key}.json`))
    );
  }

  /**
   * Create WPS and returns observable of WPS
   * currently disabled
   * @param {string} url
   * @returns {Observable<WPS>}
   */
  public create(url: string): Observable<WPS> {
    console.log('wps creation disabled');
    return null;
    // this.bar.open(`Created WPS`, 'CLOSE', { duration: 3000 });
    // return this.http.post<WPS>(`https://wpsflow.firebaseio.com/wps.json`, wps).pipe(
    //  map(obj => <WPS>wps)
    // );
  }

  /**
   * Refreshes the observable of the given WPS
   * @param {number} id
   * @param {Partial<WPS>} wps
   * @returns {Observable<WPS>}
   */
  public update(id: number, wps: Partial<WPS>): Observable<WPS> {
    this.bar.open(`Saved WPS`, 'CLOSE', { duration: 3000 });
    return this.getKeyFromId(id).pipe(
      switchMap(key => this.http.put<WPS>(`https://wpsflow.firebaseio.com/wps/${key}.json`, wps))
    );
  }

  /**
   * Removes WPS with given id
   * @param {number} id
   * @returns {Promise<boolean>}
   */
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
