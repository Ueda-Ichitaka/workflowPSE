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

  private mockWPSProvider: WPSProvider = { id: 0, title: "WPSProvider1", url: "example.com" }
  
  private testData: WPS[] = [
    {
      id: 0, provider: this.mockWPSProvider, title: "WPS1", abstract: "WPS1 Service"
    }
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

  public get(id: number): Observable<WPS> {
    return this.testObservable.pipe(
      // Map WPS[] to WPS by finding the right id
      map(data => data.find(wps => wps.id === id))
    );
  }

  public create(wps: Partial<WPS>): Observable<WPS> {
    // Assign random id to wps
    wps.id = Math.round(Math.random() * 10000000);

    // Add new WPS to WPS list
    this.testData.push(<WPS>wps);

    // Update subscriber
    this.testSubscriber.next(this.testData);

    // Return created wps
    return this.get(wps.id);
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
