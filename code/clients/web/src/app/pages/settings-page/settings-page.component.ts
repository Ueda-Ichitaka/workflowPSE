import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { ProcessService } from 'app/services/process.service';
import { WpsService } from 'app/services/wps.service';
import { WPS } from '../../models/WPS';


@Component({
  selector: 'app-settings-page',
  templateUrl: './settings-page.component.html',
  styleUrls: ['./settings-page.component.scss']
})
export class SettingsPageComponent implements OnInit {

  wps_list: Observable<WPS[]>;

  /**
   * supported language options
   */
  language_options = [
    { value: 'de', displayed: 'Deutsch' },
    { value: 'en', displayed: 'English' }
  ];

  selected_language = { value: 'de', displayed: 'Deutsch' };

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
    this.wps_list = this.wpsService.all();
  }

  /**
   * refreshes wps servers to check for
   * new processes
   */
  public refresh() {
    // TODO signal server to refresh wps services
    console.log('services refreshed');
  }

  /**
   * changes language
   * @param string
   */
  public onLangSelect(lang: { value, displayed }) {
    this.selected_language = lang;
  }

  public addWPS(url: string) {
    this.wpsService.create(url);

  }

  /**
   * removes the wps server with the given id
   * @param id the id of the wps
   */
  public remove(id: number) {
    this.wpsService.remove(id);
  }
}
