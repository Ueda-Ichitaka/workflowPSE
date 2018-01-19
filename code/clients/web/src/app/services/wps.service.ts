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

  /**
   * ----------START TEST DATA----------
   * Todo: Remove hard coded test data, and add http support when server is ready.
   */

  private mockWPSProvider: WPSProvider[] = [
    { id: 0, title: "WPSProvider1", url: "example.com" }
  ];
  
  private testData: WPS[] = [
    { id: 0, provider: this.mockWPSProvider[0], title: "WPS1", abstract: "WPS1 Service" },
    { id: 1, provider: this.mockWPSProvider[0], title: "WPS2", abstract: "WPS2 Service" },
    { id: 2, provider: this.mockWPSProvider[0], title: "WPS3", abstract: "WPS3 Service" }
  ];

  /**
   * ----------END TEST DATA----------
   */

  private testObservable: Observable<WPS[]>;
  private testSubscriber: Subscriber<WPS[]>;

  constructor(private http: HttpClient) {
      // Create test observable
      this.testObservable = new Observable(subscriber => {
      // Create test subscriber to update the observable later (in the create method)
      this.testSubscriber = subscriber;
      subscriber.next(this.testData);
    });
  }

  public all(): Observable<WPS[]> {
    return this.testObservable;
  }

  public get(id: number): Observable<WPS> {
    return this.testObservable.pipe(
      // Map WPS[] to WPS by finding the right id
      map(data => data.find(wps => wps.id === id))
    );
  }

  public create(url: string): Observable<WPS> {
    // Assign random id to wps
    var wps_id = Math.round(Math.random() * 1000);
    var provider_id = Math.round(Math.random() * 100);

    var provider_var: WPSProvider = { id: provider_id, title: `Provider${provider_id}`, url: url }
    this.mockWPSProvider.push(<WPSProvider>provider_var)

    var wps_var: WPS = { id: wps_id, provider: provider_var, title: `WPS${wps_id}`, abstract: `WPS${wps_id} Service` }

    // Add new WPS to WPS list
    this.testData.push(<WPS>wps_var);

    // Update subscriber
    this.testSubscriber.next(this.testData);

    // Return created wps
    return this.get(wps_var.id);
  }

  public update(id: number, wps: Partial<WPS>): Observable<WPS> {
    // Find wps by id
    const result = this.testData.find(p => p.id === id);

    // Update wps
    Object.assign(wps, result);

    // Update observable
    this.testSubscriber.next(this.testData);

    // Return updated wps
    return this.get(id);
  }

  public async remove(id: number): Promise<boolean> {
    // Find index by wps id
    const index = this.testData.findIndex(wps => wps.id === id);

    // Remove from array
    this.testData.splice(index, 1);

    // Update observable
    this.testSubscriber.next(this.testData);

    return true;
  }

}
