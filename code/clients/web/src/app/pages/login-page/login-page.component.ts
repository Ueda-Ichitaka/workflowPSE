import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { ProcessService } from 'app/services/process.service';
import { WpsService } from 'app/services/wps.service';
import { WPS } from '../../models/WPS';
import { trigger, transition, style, animate } from '@angular/animations';


@Component({
  selector: 'app-settings-page',
  templateUrl: './settings-page.component.html',
  styleUrls: ['./settings-page.component.scss'],
  animations: [
    trigger('slide', [
      transition(':enter', [
        style({ transform: 'translateX(-100%)' }),
        animate('233ms ease-in-out')
      ]),
      transition(':leave', [
        animate('233ms ease-in-out', style({ transform: 'translateX(100%)' }))
      ]),
    ])
  ]
})
export class SettingsPageComponent implements OnInit {

  wpsList: Observable<WPS[]>;

  @ViewChild('url')
  public urlComponent: ElementRef;

  /**
   * TODO check if processService is needed
   * creates a new settings page object
   * @param processService fetches process data
   * @param wpsService fetches wps data
   */
  constructor(
    private processService: ProcessService,
    private wpsService: WpsService,
  ) {

  }

  /**
   * is called an appropriate time after the
   * object is created, fetches wps servers
   * to display to user
   */
  public ngOnInit() {
    this.wpsList = this.wpsService.all();
  }

  /**
   * refreshes wps servers to check for
   * new processes
   */
  public async refresh() {
    await this.wpsService.refresh();
    this.wpsList = this.wpsService.all();
  }

  public async add(url: string) {
    await this.wpsService.create(url).toPromise();
    this.wpsList = this.wpsService.all();
    (<HTMLInputElement>this.urlComponent.nativeElement).value = '';
  }

  /**
   * removes the wps server with the given id
   * @param id the id of the wps
   */
  public async remove(id: number) {
    await this.wpsService.remove(id);
    this.wpsList = this.wpsService.all();
  }
}
