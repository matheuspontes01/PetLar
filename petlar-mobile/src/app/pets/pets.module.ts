import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';

import { IonicModule } from '@ionic/angular';

import { PetsPage } from './pets.page';
import { PetsPageRoutingModule } from './pets-routing.module';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    PetsPageRoutingModule
  ],
  declarations: [PetsPage]
})
export class PetsPageModule {}
